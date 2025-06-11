from matplotlib.image import imread
from IDS_Camera import *
from Image import *



# USEFUL EXAMPLES OF USE OF THE CODE:

def test5():
    # Utilizacion de la camara para tomar la imagen de un orificio circular y 
    # determinar su centro.
    camera = Camera()
    camera.start_acquisition().set_exposure(1/250)
    camera.get_image()
    picture = camera.image
    picture.display()
    picture.soften().display()
    picture.binarize().display()
    picture.search_border()
    picture.circle_treatment()
    camera.close_device()

def test7():
    # Test busqueda del centro de un fiducial de un modulos LGAD
    fig = Image(cv2.imread('./img/tfg_test/fiducial.png'))
    # fig.display(True)
    fig.binarize().display(True)
    fig.soften(8).display()
    fig.find_cm()
    fig.display(True)

def test8():
    # Test busqueda del centro de un fiducial de un modulos LGAD
    fig = Image(cv2.imread('./img/tfg_test/circ1.png'))
    # fig.binarize().display()
    fig.soften(2).binarize(1.5).display(True)
    fig.search_border(show=True, save=True)
    fig.circle_treatment(show=True, save=True)

def test9():
    # TEST: busqueda del centro de un circulo
    fig = Image(cv2.imread('./img/tfg_test/circ2.png'))
    # fig.binarize().display()
    fig.soften(16).binarize(2.5).display(True)
    fig.search_border(show=True, save=True)
    fig.circle_treatment(show=True, save=True)


def main():

    # test5()
    # test7()
    # test8()
    test9()
    


if __name__ == "__main__":

    main()

    

    



    

