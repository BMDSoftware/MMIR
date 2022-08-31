#import urllib.request
import pyvips

#URL = 'http://www.rollthepotato.net/~john/IMG_2420.JPG'

#input_file = urllib.request.urlopen(URL)

# pyvips will use this to fetch bytes from the URL
#def read_handler(size):
 #   return input_file.read(size)

# 'sequential' means stream the image during processing
#source = pyvips.SourceCustom()
#source.on_read(read_handler)

#image = pyvips.Image.new_from_source(source, '', access='sequential')

#img_color = cv2.imread("../media/img/moving/M32_R2_II.png")

#array_rgb = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)




image = pyvips.Image.new_from_file("../media/img/moving/M32_R2_II.png")



image.dzsave(
        "test_zoom1",
        layout="dz",
        basename ="test",
        suffix=".png",
        tile_size=1024,
        overlap=0,
        depth="onepixel",
        properties=False
    )


