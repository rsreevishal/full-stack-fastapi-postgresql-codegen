class FileHandler:
    @staticmethod
    def get_body(file_path, smark, emark, skip_start=False):
        f = open(file_path, "r")
        content = f.read()
        start = content.find(smark)
        end = content.find(emark)
        f.close()
        if not skip_start:
            return content[start: end]
        else:
            return content[start+len(smark): end]

    @staticmethod
    def writeTo(file_path, content):
        f = open(file_path, "w")
        f.write(content)
        f.close()
