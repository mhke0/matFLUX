import os
import re
import numpy as np
from scipy.io import savemat
import sys

# Attempt to import zarr, exit if unavailable
try:
    import zarr
except ImportError:
    print("Error: zarr module not found. Please install with: pip install zarr")
    sys.exit(1)


def sanitize_field(name):
    """
    Replace non-alphanumeric characters with underscores and
    prefix with 'm_' if the name begins with a digit.
    """
    s = re.sub(r'[^0-9a-zA-Z]', '_', name)
    if re.match(r'^[0-9]', s):
        s = 'm_' + s
    return s


def find_zarr_path(subdir_path, subdir_name):
    """
    Locate a Zarr archive inside a measurement folder.
    """
    # Check if root is a zarr archive (new format)
    if (os.path.exists(os.path.join(subdir_path, '.zgroup')) or
        os.path.exists(os.path.join(subdir_path, '.zattrs')) or
        any(os.path.isdir(os.path.join(subdir_path, d)) for d in ['grd', 'mbm', 'mfx'])):
        return subdir_path

    # Fallback old-format locations
    candidates = [
        os.path.join(subdir_path, 'zarr', 'grd', 'mbm'),
        os.path.join(subdir_path, 'zarr'),
        os.path.join(subdir_path, 'data', 'zarr'),
        os.path.join(subdir_path, 'mbm')
    ]
    for path in candidates:
        if os.path.exists(path) and \
           (os.path.exists(os.path.join(path, '.zgroup')) or os.path.exists(os.path.join(path, '.zattrs'))):
            return path
    return None


def extract_new_format_beads_from_points(points_array, used_beads, subdir_name):
    """
    Map consolidated points array to per-bead localization lists.
    """
    subdir_data = {}
    try:
        # Load array and group by grid index 'gri'
        data = points_array[:]
        if 'gri' not in data.dtype.names:
            return {}
        bead_groups = {}
        for rec in data:
            gri = rec['gri']
            bead_groups.setdefault(gri, []).append(rec)
        # Determine good grids (>10 points)
        good_grids = [gri for gri, pts in bead_groups.items() if len(pts) > 10]
        sorted_beads = sorted(used_beads)
        # Map one-to-one in order
        for i, bead_name in enumerate(sorted_beads):
            if i < len(good_grids):
                pts = bead_groups[good_grids[i]]
                locs = [{'pos': p['xyz'], 'tim': float(p['tim'])} for p in pts]
                subdir_data[bead_name] = locs
    except Exception as e:
        print(f"Error in new-format mapping for {subdir_name}: {e}")
    return subdir_data


def extract_new_format_beads(archive, subdir_name, subdir_path):
    """
    Extract beads from a new-format Zarr archive (consolidated points).
    """
    # Find 'used' metadata
    used_beads = None
    for loc in ['mbm', 'grd/mbm']:
        parts = loc.split('/')
        cur = archive
        for p in parts:
            if p in cur:
                cur = cur[p]
            else:
                break
        else:
            if 'used' in getattr(cur, 'attrs', {}):
                used_beads = cur.attrs['used']
                break
    if not used_beads and 'used' in getattr(archive, 'attrs', {}):
        used_beads = archive.attrs['used']
    if not used_beads:
        return {}
    # Find points array
    points = None
    for loc in ['grd/mbm/points', 'mbm/points', 'points']:
        parts = loc.split('/')
        cur = archive
        for p in parts:
            if p in cur:
                cur = cur[p]
            else:
                break
        else:
            if hasattr(cur, 'shape'):
                points = cur
                break
    if points is None:
        return {}
    return extract_new_format_beads_from_points(points, used_beads, subdir_name)


def extract_old_format_beads(archive, subdir_name):
    """
    Extract beads from an old-format Zarr archive (individual datasets).
    """
    subdir_data = {}
    try:
        for ds in archive:
            if not ds.startswith('R'):
                continue
            arr = archive[ds]
            data = arr[:] if hasattr(arr, '__getitem__') else arr.get()
            locs = []
            if data.dtype.names:
                for rec in data:
                    pos = rec['pos'] if 'pos' in rec.dtype.names else rec[1]
                    tim = float(rec['tim']) if 'tim' in rec.dtype.names else float(rec[0])
                    locs.append({'pos': pos, 'tim': tim})
            else:
                for row in data:
                    if len(row) >= 2:
                        locs.append({'pos': row[1], 'tim': float(row[0])})
            if locs:
                subdir_data[ds] = locs
    except Exception as e:
        print(f"Error in old-format extraction for {subdir_name}: {e}")
    return subdir_data


def extract_bead_data(archive, subdir_name, subdir_path):
    """
    Try new format first, then fall back to old format.
    """
    try:
        data = extract_new_format_beads(archive, subdir_name, subdir_path)
        if data:
            return data
        data = extract_old_format_beads(archive, subdir_name)
        return data or {}
    except Exception as e:
        print(f"Error extracting bead data from {subdir_name}: {e}")
        return {}


def convert_to_matlab_format(all_data):
    """
    Convert nested dict of lists into nested dict of NumPy structured arrays.
    """
    out = {}
    for meas, beads in all_data.items():
        bead_structs = {}
        for bead, locs in beads.items():
            if not isinstance(locs, list) or not locs:
                continue
            n = len(locs)
            arr = np.zeros(n, dtype=[('pos', 'f8', (3,)), ('tim', 'f8')])
            for i, rec in enumerate(locs):
                arr[i]['pos'] = rec['pos']
                arr[i]['tim'] = rec['tim']
            bead_structs[bead] = arr
        if bead_structs:
            out[meas] = bead_structs
    return out


def find_valid_directory():
    """
    Auto-detect a parent directory with subfolders.
    """
    candidates = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'data'),
        os.path.join(os.getcwd(), 'example'),
        os.path.dirname(os.getcwd())
    ]
    if len(sys.argv) > 1:
        candidates.insert(0, sys.argv[1])
    for d in candidates:
        if os.path.isdir(d):
            subs = [x for x in os.listdir(d)
                    if os.path.isdir(os.path.join(d, x))
                       and not x.startswith('.')
                       and x != '__pycache__']
            if subs:
                print(f"Using directory: {d}")
                return d
    print("Error: Could not find a valid data directory.")
    return None


def save_localizations_to_common_mat(parent_directory, output_file=None):
    """
    Scan subfolders, extract bead logs, sanitize names, and save to .mat
    """
    all_data = {}
    subs = []
    for sub in os.listdir(parent_directory):
        sp = os.path.join(parent_directory, sub)
        if os.path.isdir(sp) and sub != '__pycache__':
            subs.append(sub)
            zp = find_zarr_path(sp, sub)
            if zp:
                try:
                    arc = zarr.open(zp, 'r')
                    bd = extract_bead_data(arc, sub, sp)
                    if bd:
                        all_data[sub] = bd
                        print(f"Extracted {len(bd)} beads from {sub}")
                except Exception as e:
                    print(f"Failed {sub}: {e}")
            else:
                print(f"No Zarr in {sub}")
        else:
            if sub != '__pycache__': 
                print(f"Skipping {sub}")
    if not all_data:
        print("No data collected.")
        return None

    # Output filename
    if output_file:
        out_file = output_file
    else:
        home = os.path.expanduser('~')
        tag = '_'.join(sorted(subs))
        out_file = os.path.join(home, f'correction_{tag}.mat')
    odir = os.path.dirname(out_file)
    if odir and not os.path.exists(odir):
        os.makedirs(odir, exist_ok=True)

    # Convert and sanitize
    matlab_data = convert_to_matlab_format(all_data)
    clean = {}
    for m, bdict in matlab_data.items():
        sm = sanitize_field(m)
        clean[sm] = {}
        for b, arr in bdict.items():
            clean[sm][sanitize_field(b)] = arr

    # Save
    try:
        print(f"Saving to {out_file}...")
        savemat(out_file, {'data': clean}, format='5', do_compression=True)
        print(f"Saved to {out_file}")
        return out_file
    except Exception as e:
        print(f"Error saving .mat: {e}")
        return None


if __name__ == '__main__':
    print("ZARR Bead Data Extractor")
    print("Supports both old and new ZARR formats")
    print("="*50)

    if len(sys.argv) >= 3:
        parent, outp = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        parent, outp = sys.argv[1], None
    else:
        parent, outp = find_valid_directory(), None

    if not parent:
        sys.exit(1)
    res = save_localizations_to_common_mat(parent, outp)
    if res:
        print("SUCCESS:", res)
        sys.exit(0)
    else:
        print("FAILED to save data.")
        sys.exit(1)
