
class MavenOutputParser(object):

    def parse(self, output: str):
        lines = output.split("\n")
        out = []
        for line in lines:
            line = line.strip()
            # print(line)
            # if line.startswith("[INFO]"):
            #     out.append(MavenOutputLine("info", line[6:].strip()))
            # elif line.startswith("[ERROR] /D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"):
            #     start_index = str(line).index("[", 10)
            #     out.append(MavenOutputLine("idx", line[start_index:].strip()))#这个可以每种编译错误都拿来提示，也可以只在参数类型和数目不匹配配合提示
            if line.startswith("符号:   类 "):
                # print({"notfound_class": line[8:].strip()})
                out.append({"notfound_class": line[8:].strip()})
                break
            elif line.startswith("符号:   方法 "):
                # print({"notfound_API": line[9:].strip()})
                out.append({"notfound_API": line[9:].strip()})
            elif line.startswith("位置: 类"):
                # print({"notfound_API_location": line[3:].strip()})
                out.append({"notfound_API_location": line[3:].strip()})
                break
            # elif line.startswith("      (参数不匹配"):
            #     out.append(MavenOutputLine("API_para_type_error", "方法参数类型不匹配"))
            # elif line.startswith("      (实际参数列表和形式参数列表长度不同)"):
            #     out.append(MavenOutputLine("API_para_num_error", "方法参数个数不匹配"))
            elif line.startswith("[ERROR] Tests run"):
                start_index = line.index("Failures: ")
                end_index = line.index(",", start_index)
                out.append({"failed_num": line[start_index+10:end_index].strip()})
            elif line.startswith('[ERROR]   ') and '\"' in line:
                out.append({"error_rules_info": line.strip()})
                 # 选第一个没过的测试用例
            # elif line.startswith("[ERROR]"):
            #     out.append(MavenOutputLine("error", line))
            # else:
            #     out.append(MavenOutputLine("else", line))


            # if "BUILD FAILURE" in line:
            #     out.status = "failure"
            #     break
            # elif "BUILD SUCCESS" in line:
            #     out.status = "success"
            #     break

        return out