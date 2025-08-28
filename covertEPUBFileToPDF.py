# import OS
import os

from epub2pdf import EpubPdfConverter
# for x in os.listdir("D://"):
#     if x.endswith(".epub"):
#         # Prints only text file present in My Folder
#         print(x)
#         print("Converting "+x)
#         epb = EpubPdfConverter("D://"+x, "D://"+x+".pdf","SinglePagels","SinglePage","R2L")
#         epb.convert()

srcFile = "C://Users//Mahesh//Downloads//(Day Trader), Christopher - Price Action Scalping Strategy _ option scalping - By Christopher (Day Trader) - Only For Genuine Day Trader _ Make Money with price action Based Strategy _-UNKNOWN (2024).epub"


epb = EpubPdfConverter(srcFile, "D://Price Action Scalping Strategy _ option scalping - By Christopher.pdf","SinglePagels","SinglePage","R2L")
epb.convert()