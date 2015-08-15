import sys, getopt

def parse_args():
    argv = sys.argv[1:]
    in_path = None
    out_file = None
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--input"):
            in_path = arg
        elif opt in ("-o", "--output"):
            out_file = arg
    return in_path, out_file

