import h5py
from pathlib import Path
import pandas as pd
from dateutil import parser
from argparse import ArgumentParser


def get_stats(bulkfile):
    file = h5py.File(bulkfile, "r")
    s_dict = {}
    try:
        s_dict['sample_frequency'] = int(file["UniqueGlobalKey"]["context_tags"].attrs["sample_frequency"].decode('utf8'))
    except KeyError:
        s_dict['sample_frequency'] = "NA"
    try:
        s_dict['run_id'] = file["UniqueGlobalKey"]["tracking_id"].attrs["run_id"].decode('utf8')
    except KeyError:
        s_dict['run_id'] = "NA"
    try:
        s_dict['experiment'] = file["UniqueGlobalKey"]["tracking_id"].attrs["sample_id"].decode('utf8')
    except KeyError:
        s_dict['experiment'] = "NA"
    try:
        s_dict['flowcell_id'] = file["UniqueGlobalKey"]["tracking_id"].attrs["flow_cell_id"].decode('utf8')
    except KeyError:
        s_dict['flowcell_id'] = "NA"
    try:
        s_dict['minknow_version'] = file["UniqueGlobalKey"]["tracking_id"].attrs["version"].decode('utf8')
    except KeyError:
        s_dict['minknow_version'] = "NA"
    try:
        s_dict['minion_id'] = file["UniqueGlobalKey"]["tracking_id"].attrs["device_id"].decode('utf8')
    except KeyError:
        s_dict['minion_id'] = "NA"
    try:
        s_dict['hostname'] = file["UniqueGlobalKey"]["tracking_id"].attrs["hostname"].decode('utf8')
    except KeyError:
        s_dict['hostname'] = "NA"
    try:
        s_dict['sequencing_kit'] = file["UniqueGlobalKey"]["context_tags"].attrs["sequencing_kit"].decode('utf8')
    except KeyError:
        s_dict['sequencing_kit'] = "NA"
    try:
        s_dict['flowcell_type'] = file["UniqueGlobalKey"]["context_tags"].attrs["flowcell_type"].decode('utf8')
    except KeyError:
        s_dict['flowcell_type'] = "NA"
    try:
        s_dict['asic_id'] = file["UniqueGlobalKey"]["tracking_id"].attrs["asic_id"].decode('utf8')
    except KeyError:
        s_dict['asic_id'] = "NA"
    try:
        s_dict['experiment_start'] = parser.parse(
            file["UniqueGlobalKey"]["tracking_id"].attrs["exp_start_time"].decode('utf8')).strftime(
            '%d-%b-%Y %H:%M:%S')
    except KeyError:
        s_dict['experiment_start'] = "NA"
    return s_dict


def main():
    args = get_args()

    p = Path(args.dir)
    files = [x.name for x in p.iterdir() if x.suffix == '.fast5']
    for index, file in enumerate(files):
        bulk_file = h5py.File(Path(Path(args.dir) / file), 'r')
        try_path = bulk_file["Raw"]
        for i, channel in enumerate(try_path):
            if i == 0:
                try:
                    try_path[channel]["Signal"][0]
                except KeyError:
                    del files[index]
            break
        bulk_file.flush()
        bulk_file.close()

    header = ['sample_frequency', 'run_id', 'experiment', 'flowcell_id', 'minknow_version', 'minion_id',
              'hostname', 'sequencing_kit', 'flowcell_type', 'asic_id', 'experiment_start']
    df = pd.DataFrame(columns=header)
    
    for file in files:
        df = df.append(get_stats(Path(p / file)), ignore_index=True)

    df.to_csv(args.out, sep=",", header=header, index=False)

def get_args():
    parser = ArgumentParser(
        description="""Given a directory containing bulk fast5 files output a csv containing the run 
        information for them""",
        add_help=False)
    general = parser.add_argument_group(
        title='General options')
    general.add_argument("-h", "--help",
                         action="help",
                         help="Show this help and exit"
                         )
    in_args = parser.add_argument_group(
        title='Input sources'
    )
    in_args.add_argument("-d", "--dir",
                         help="A directory containing bulk-fast5-files",
                         type=str,
                         default='',
                         required=True,
                         metavar=''
                         )
    out_args = parser.add_argument_group(
        title='Output sources'
    )
    out_args.add_argument("-o", "--out",
                         help="Output csv filename",
                         type=str,
                         default='',
                         required=True,
                         metavar=''
                         )
    return parser.parse_args()


if __name__ == '__main__':
    main()