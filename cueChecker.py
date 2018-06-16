import os
import sys

ROOT_DIR = "."

def main():

    passed = open("pass.txt", "w")

    albums = []
    for root, dirs, files in os.walk(ROOT_DIR):
        print(dirs, file=sys.stderr)
        for f in files:
            if ".cue" in f:
                names = f[:-4].split(" - ")
                record_dict = {
                    "basename": f[:-4],
                    "artist": names[0],
                    "album": names[1],
                    "basic_pass": True,
                    "title_pass": True,
                    "songs": []
                }
                file_path = os.path.join(root, f)
                album = file_checker(file_path, record_dict)
                albums.append(album)

    for album in albums:
        if album["basic_pass"] is False:
            print(album, '\n')

    for album in albums:
        if album["title_pass"] is False:
            print(album , '\n')
    
    year_catalog = {}
    for album in albums:
        if "year" in album:
            year = album["year"]
            if year in year_catalog:
                year_catalog[year].append(album["album"])
            else:
                year_catalog[year] = [album["album"]]
    
    genre_catalog = {}
    for album in albums:
        if "genre" in album:
            genre = album["genre"]
            if genre in genre_catalog:
                genre_catalog[genre].append(album["album"])
            else:
                genre_catalog[genre] = [album["album"]]

    passed.write(str(year_catalog))
    passed.write('\n')

    passed.write(str(genre_catalog))
    passed.write('\n')

    for album in albums:
        if album["basic_pass"] and album["title_pass"]:
            passed.write(str(album))
            passed.write('\n')

    passed.close()


def file_checker(file_path, record_dict):
    fin = open(file_path, 'r')
    in_lines = fin.readlines()
    fin.close()

    existence = {
        "genre": False,
        "year": False,
        "artist": False,
        "album": False,
        "filename": False
    }

    for line in in_lines:

        if "PERFORMER “" in line or "TITLE “" in line or "FILE “" in line:
            record_dict["basic_pass"] = False
            record_dict["basic_fail_reason"] = "chinese quotation mark"
            return record_dict

        if "REM GENRE" in line:
            if existence["genre"] is True:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "genre repeat"
                return record_dict
            else:
                record_dict["genre"] = line.strip('\n')[10:]
                existence["genre"] = True

        elif "REM DATE" in line:
            if existence["year"] is True:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "year repeat"
                return record_dict
            else:
                record_dict["year"] = line.strip('\n')[9:]
                existence["year"] = True

        elif "PERFORMER" in line and line[0] != ' ':
            if line[-2] != '"':
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = " performer quotation mark missing"
                return record_dict
            artist = line[11:].strip("\"\n")
            if existence["artist"] is True:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "artist repeat"
                return record_dict
            elif artist != record_dict["artist"]:
                    record_dict["basic_pass"] = False
                    record_dict["basic_fail_reason"] = "artist not matching\n" + artist + '\n' + record_dict["artist"]
                    return record_dict
            else:
                existence["artist"] = True
        
        elif "TITLE" in line and line[0] != ' ':
            if line[-2] != '"':
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "album quotation mark missing"
                return record_dict
            album_name = line[7:].strip("\"\n")
            if existence["album"] is True:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "artist repeat"
                return record_dict
            elif album_name != record_dict["album"]:
                    record_dict["basic_pass"] = False
                    record_dict["basic_fail_reason"] = "album not matching\n" + album_name + '\n' + record_dict["album"] 
                    return record_dict
            else:
                existence["album"] = True
        
        elif "FILE" in line and "\" WAVE" in line:
            if line[-7:] != "\" WAVE\n":
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "filename quotation mark missing"
                return record_dict
            filename = line[6:-7]
            if ".flac" not in filename:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "flac missing"
                return record_dict
            elif existence["filename"] is True:
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "filename repeat"
                return record_dict
            else:
                filename = filename[:-5]
                if filename != record_dict["basename"]:
                    record_dict["basic_pass"] = False
                    record_dict["basic_fail_reason"] = "basename not matching\n" + filename + '\n' + record_dict["basename"]
                    return record_dict
                else:
                    existence["filename"] = True
        
        elif "   TITLE" in line:
            if line[-2] != '"':
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "title quotation mark missing"
                return record_dict
            song = line[11:].strip("\"\n")
            record_dict["songs"].append(song)

        elif "    PERFORMER" in line:
            if line[-2] != '"':
                record_dict["basic_pass"] = False
                record_dict["basic_fail_reason"] = "title performer quotation mark missing"
                return record_dict
            artist = line[15:].strip("\"\n")
            if artist != record_dict["artist"]:
                    record_dict["title_pass"] = False
                    record_dict["title " + record_dict["songs"][-1]] = "artist"

    for key, value in existence.items():
        if not value:
            record_dict["basic_pass"] = False
            record_dict["basic_fail_reason"] = key + " missing"

    return record_dict

if __name__ == "__main__":
    main()
