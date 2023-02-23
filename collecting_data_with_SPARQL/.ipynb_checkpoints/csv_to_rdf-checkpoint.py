# code à verifier 
def transform_csv_line(csv_str):
    res = ""
    for word in csv_str.split(" ,\n"):
        res += "<"
        res += word
        res += "> "
    res += ".\n"


def csv_to_rdf(input_file, output_file):
    f = open(input_file)
    res = open(output_file, "w")
    strcolumns = f.readline()
    nb_columns = strcolumns.count(',')
    for line_csv in f.readlines():
        res.write(transform_csv_line(line_csv))
    
