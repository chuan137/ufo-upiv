import sys, getopt

def parse_args():
    argv = sys.argv[1:]
    result = dict()

    def print_helper():
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit()

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
        print opts
        print args
    except getopt.GetoptError:
        print_helper()

    for opt, arg in opts:
        if opt == '-h':
            print_helper()
        elif opt in ("-i", "--input"):
            result['in_path'] = arg
        elif opt in ("-o", "--output"):
            result['out_file'] = arg
        else:
            result[opt] = arg

    return result

