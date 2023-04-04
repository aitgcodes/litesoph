import sys
from argparse import ArgumentParser

def parse_input(td_dict, lines):
    
    labels = td_dict.get('labels')
    pol = td_dict.get('polarization')

    data = []
    for l in lines:
        if all ([tag in l for tag in labels]):
            try:
                vals = l.strip().split('#')[0].split()
            except:
                raise Exception ("Failed to parse line: {0}".format(l))

            try:
                if pol:
                    data.append([float(vals[1]), float(vals[pol[1]])])
                else:
                    data.append([float(d) for d in vals[1:]])
            except:
                raise Exception ("Failed to convert data line: {1}".format(l))

    ndata = len(data)

    if ndata <= 0:
        raise Exception ("Failed to find any data, check target and options.")
         
    return data

    
def postprocess_check(write, args, data):
    
    tprev = -9999.0
    d0 = data[0][1]

    for d in data:
        t = d[0]
        
        if abs(t - tprev) < 1e-6:
            raise Exception ("Error: Repeating times found--ambiguous target.  Multiple geometries?  Using closedshell target for openshell or spin-orbit?")

        tprev = t

        if args.zero:
            d[1] = d[1] - d0

    if args.header and args.zero:
        write("# Postprocessing: zeroed at first time point")

    return data

def write_td_output(write, data, td_dict):
    pol = td_dict.get('polarization') 
    target = td_dict.get('target')
    
    if target != 'moocc':
  
        write("#\n")
        write("#-----------------------------------------\n")
        
        if pol:
            tag = target + '_' + pol[0]
            write("#   Time [au]        {0} [au]         \n".format(tag))
        else:
            tag = [f'{target}_x', f'{target}_y', f'{target}_z']
            write("#   Time [au]        {} [au]         {} [au]         {} [au]\n".format(*tag))
        
        write("#-----------------------------------------\n")
        write("#\n")

    for d in data:
        txt = "     {: .10e}" * len(d) + '\n'
        write(txt.format(*d))


def check_args_determine_labels(td_dict):
    """Check arguments and generate tags for parsing the output"""
    labels = td_dict['labels'] = []
    target = td_dict.get('target')
    tag = td_dict.get('tag')

    labels.append(tag)
    ## do these outputs have x,y,z values, geom, spin tags etc?
    spin = False
    geom = False

    ## data type
    if target == "dipole":
        labels.append("Dipole moment")
        spin = True
        geom = True
        
    elif target == "efield":
        labels.append("Applied E-field")
        spin = True
        geom = True

    elif target == "energy":
        labels.append("Etot")

    elif target == "S2":
        labels.append("S^2")

    elif target == "charge":
        labels.append("Charge")
        spin = True
        geom = True
    
    elif target == "moocc":
        labels.append("MO Occupations")
    else:
        raise Exception ("Invalid target: {0}".format(target))

    if td_dict.get('polarization'):
        if td_dict.get('polarization') == "x":
            td_dict['polarization'] = ('x', 2)
        elif td_dict.get('polarization') == "y":
            td_dict['polarization'] = ('x', 3)
        elif td_dict.get('polarization') == "z":
            td_dict['polarization'] = ('x', 4)

    ## spin type
    if spin:
        if td_dict.get('spin') == "closedshell":
            pass
        elif td_dict.get('spin') == "alpha":
            labels.append("(alpha spin)")
        elif td_dict.get('spin') == "beta":
            labels.append("(beta spin)")
        elif td_dict.get('spin') == "total":
            labels.append("(total spin)")
        else:
            raise Exception ("Invalid spin type: {0}".format(spin))
    else:
        pass
    
    ## geom
    if geom:
        labels.append(td_dict.get('geometry'))
    else:
        pass
  
    return td_dict

def p(txt):
    txt = txt.strip('\n')
    print(txt)


def nwchem_rt_parser(td_out_file, outfile=None, tag='<rt_tddft>',
                    geometry='system', 
                    target='dipole', spin='closedshell', 
                    polarization=None, zero=False, retrun_data=False):
    
    td_dict = dict(tag=tag,
                    geometry=geometry,
                    target=target,
                    spin=spin,
                    polarization=polarization,
                    zero=zero)

    if outfile:
        f = open(outfile, 'w')
        write = f.write
    else:
        write = p

    td_dict = check_args_determine_labels(td_dict)

    try:
        with open(td_out_file, 'r') as f:
            lines = f.readlines()
    except:
        raise Exception(f'Failed to read in data from file: {td_out_file}')
    
    data = parse_input(td_dict, lines)

    if retrun_data:
        return data

    write("#======================================\n")
    write("#  NWChem Real-time TDDFT output parser\n")
    write("#======================================\n")
    write("# \n")
    
    write("# ------\n")
    write('# Filename: "{0}"\n'.format(td_out_file))
    write("#-------\n")

    write("# Number of data points: {0}\n".format(len(data)))
    write("# Time range: [{0}: {1}]\n".format(data[0][0], data[-1][0]))

    write_td_output(write, data, td_dict)

    if outfile:
        f.close()

def main ():

    parser = ArgumentParser(description="Parse NWChem real-time TDDFT output for time-dependent quantities.")
    
    parser.add_argument('nw_file', help = "NWchem rt tddft output file")
    parser.add_argument("-o", '--out_file', help= "Output file.")
    parser.add_argument("-t", "--tag", type=str, dest="tag",
                       help="parse for simulation tag STR, defaults to '<rt_tddft>'", metavar="STR")
    parser.add_argument("-g", "--geometry", type=str, dest="geom",
                       help="extract data for geometry STR, defaults to 'system'", metavar="STR")
    parser.add_argument("-x", "--extract", type=str, dest="target",
                       help="target data to extract: dipole (default), efield, energy, S2, charge, moocc", metavar="STR")
    parser.add_argument("-p", "--polarization", type=str, dest="polarization",
                       help="target polarization: x (default), y, z", metavar="STR")
    parser.add_argument("-s", "--spin", type=str, dest="spin",
                       help="target spin: closedshell (default), alpha, beta, total", metavar="STR")
    parser.add_argument("-C", "--clean", action="store_false", dest="header",
                      help="clean output; data only, no header or comments")
    parser.add_argument("-z", "--zero", action="store_true", dest="zero",
                      help="zero data at t=0")
    parser.set_defaults(out_file = None, tag = "<rt_tddft>", geom = "system", target = "dipole",polarization=None,
                        spin="closedshell", header = True, zero = False)

    
    args = parser.parse_args()
    
    nwchem_rt_parser(args.nw_file, args.out_file, tag=args.tag, geometry=args.geom,
                    target= args.target, spin= args.spin, polarization=args.polarization,
                    zero=args.zero)
    
    
if __name__ == "__main__":
    main()
