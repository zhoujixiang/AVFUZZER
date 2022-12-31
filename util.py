def print_debug(info):
    with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/result/record.txt','a+') as f:
        f.write(info)
        f.write("\n")

def write_individual(position,vehicle,weather):
    with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/result/individual.txt', 'a') as f:
        f.write(position+vehicle+weather)
        f.write("\n")

def read_individual():
    with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/result/individual.txt', 'ra') as f:
        pass

if __name__ == "__main__":
    s="hello"
    a="world"
    b="!"
    write_individual(s,a,b)

