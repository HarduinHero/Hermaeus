def response_content_cleaner(content:bytes, bodytype:str="json") -> str :
    str_content = content.decode("utf-8", "ignore")
    if bodytype == "json" :
        first_char_index, last_char_index = None, None
        for i in range(len(str_content)) :
            if first_char_index is None and (str_content[i] == "{" or str_content[i] == "[") :
                first_char_index = i
            if last_char_index is None and (str_content[len(str_content)-1-i] == "}" or str_content[len(str_content)-1-i] == "]") :
                last_char_index = len(str_content)-i
            if first_char_index is not None and last_char_index is not None :
                return str_content[first_char_index:last_char_index]
    return str_content