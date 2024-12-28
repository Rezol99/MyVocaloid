from file_encoder import FileEncoder

TARGET_DIR = "./thirdparty/「波音リツ」歌声データベースVer2/DATABASE"
OUTPUT_DIR = "./master/ust/json"

MIN_PITCH = 30
MAX_PITCH = 100

if __name__ == "__main__":
    encoder = FileEncoder(TARGET_DIR, MIN_PITCH, MAX_PITCH, OUTPUT_DIR)
    encoder.encode()