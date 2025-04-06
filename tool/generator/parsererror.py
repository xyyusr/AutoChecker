
class MavenOutputParser(object):
    def parse(self, output: str):
        lines = output.split("\n")
        out = []
        for line in lines:
            line = line.strip()
            if line.startswith("符号:   类 "):
                out.append({"notfound_class": line[8:].strip()})
                break
            elif line.startswith("符号:   方法 "):
                out.append({"notfound_API": line[9:].strip()})
            elif line.startswith("位置: 类"):
                out.append({"notfound_API_location": line[3:].strip()})
                break
            elif line.startswith("[ERROR] Tests run"):
                start_index = line.index("Failures: ")
                end_index = line.index(",", start_index)
                out.append({"failed_num": line[start_index+10:end_index].strip()})
            elif line.startswith('[ERROR]   ') and '\"' in line:
                out.append({"error_rules_info": line.strip()})

        return out