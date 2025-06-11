"""
Script defining Image class. Enables processing of 
taken images. Uses CircleCompleter in order to calculate the center of circles given an image
of just a portion.

Author: Raul Penagos
Date: Feb 13th, 2025
"""

import numpy as np
from matplotlib import pyplot as plt
import datetime as dt
from CircleCompleter import CircleFit
import cv2
import os # path to the project, used in Image.save()


class Image:
    """
    Class Image, helps in foramting and processing pictures taken with an IDS camera.
    Methods of the class:
    save()    display()   binarize()  soften()    find_cm()   search_border()  circle_treatment()

    Para facilitar la minimaización definir unos valores iniciales del centro acorde con lo esperado
    """
    def __init__(self, matrix):
        self.image = np.copy(matrix[:,:,0])
        self.image_original = np.copy(matrix)
        self.timestamp = dt.datetime.now()
        self.file_name = f'img/tfg_test/img_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.png'

        dirname = os.path.dirname(__file__)  # Edit where to save the img
        self.abs_filename = os.path.join(dirname, self.file_name)

        self.cm = (None, None)


    def save(self):
        """
        Save the image to the file name given by the Image's time stamp.
        Make sure the folder exists.
        """
        plt.figure(figsize = (5,5))
        plt.imshow(self.image)
        
        plt.savefig(self.abs_filename, bbox_inches='tight', pad_inches=0)

    def display(self, save = False):
        """
        Show and optionally save the image on screen.
        """
        plt.close("all")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(self.image, cmap='gray')
        ax.axis('off')  # Oculta ejes y ticks

        if self.cm != (None, None):
            ax.plot(self.cm[0], self.cm[1], 'or')

        if save:
            plt.savefig(self.abs_filename, bbox_inches='tight', pad_inches=0)

        plt.show()


    def binarize(self, tresh: float = 2):
        """
        Binarize the image to (0, 255) grey scale (black and white).
        """
        self.image = np.where(self.image > self.image.max()/tresh, 255, 0)
        return self
        
    def soften(self, m = 8 ):
        """
        Soften filter smoothens the image by taking and average of a m shape
        square kernel.
        """
        # Average filter
        for i in range(0+m, self.image.shape[0] - m):
            for j in range(0+m, self.image.shape[1] - m):
                self.image[i,j] = np.mean(self.image[i-m:i+m, j-m:j+m])
        return self
    
    def find_cm(self):
        """
        Given a binarized picture, it subtracts the center of fiducials (white) 
        on a black Background.
        """
        # Average of white Pixels, for binarized pictures 
        yy, xx = np.where(self.image > 0)
        # self.cm = np.array([xx, yy])
        self.cm = (xx.mean(), yy.mean()) if xx.size > 0 else (None, None)
             
    def search_border(self, show = True, save = False):
        """
        Busca los pixels de frontera en una imagen binarizada, aquellos que estén rodeados 
        por pixels de distinto color. (up, down, right, left)
        Si hago una cruz con 'brazos mas largos' y exijo que dos sean negros y dos blancos
        podría mejorar y quitarme tantos puntos de ruido
        """
        # Defino frontera
        y_max , x_max = np.asarray(self.image.shape) - 1

        # Desplazamientos en las 4 direcciones principales
        up    = np.roll(self.image, shift=-1, axis=0)
        down  = np.roll(self.image, shift=1, axis=0)
        left  = np.roll(self.image, shift=1, axis=1)
        right = np.roll(self.image, shift=-1, axis=1)

        print(self.image.max())
        print(self.image.min()) 

        # Detectar bordes: puntos donde hay un 1 y algún vecino es 0
        # border_mask = (self.image == 1) & ((up == 0) | (down == 0) | (left == 0) | (right == 0))
        border_mask = (self.image == 0) & ((up > 0) | (down > 0) | (left > 0) | (right > 0))

        # Obtener coordenadas de los bordes
        y, x = np.where(border_mask)

        # Quito elementos de los bordes de imagen
        index_x = np.copy([i for i, xx in enumerate(x) if (xx <= 1 or xx >= x_max)])
        if len(index_x) != 0:
            y = np.delete(y, index_x)
            x = np.delete(x, index_x)

        index_y = np.copy([i for i, xx in enumerate(y) if (xx <= 1 or xx >= y_max)])
        if len(index_y) != 0:
            y = np.delete(y, index_y)
            x = np.delete(x, index_y)


        if show:
            plt.plot(x, y, 'ro') 
            plt.imshow(self.image, cmap = 'gray')   
            if save:
                plt.savefig('./img/tfg_test/border.png', bbox_inches='tight', pad_inches=0)
            plt.show()

        return x, y
    
    def canny(self):
        """
        No funciona bien con imagenes binarizadas, el algoritmo no lo permite
        """

        # fig = cv2.imread('./biblia.jpg')[: , :, 0]
        # fig = imread('./biblia.jpg')[: , :, 0]
        fig = self.image

        bordeCanny = cv2.Canny(fig, 100, 200)

        cv2.imshow('Original', fig)
        cv2.imshow('Canny', bordeCanny)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        x, y = np.array([]), np.array([])
        for i,f in enumerate(bordeCanny):
            for j,px in enumerate(f):
                if px != 0:
                    x = np.append(x, j)
                    y = np.append(y, np.abs(i-800))

        plt.plot(x,y , 'or')

        # plt.gca().invert_yaxis()
        plt.show()

        return x,y
 
    def circle_treatment(self, show = True, save = False):
        """
        Given the coordinates x,y of a circles border, or segment of its border
        It will minimize through a Likelihood function the center (a,b) of the 
        circle and its radius (r).
        Returns: 
            a: posición centro en x
            b: posición centro en y
        """
        x, y = self.search_border()

        cal = CircleFit(x, y)

        results = cal.fit()    

        print(results.summary())

        print(results.params)

        a, b, r = results.params

        if show:
            plt.imshow(self.image, cmap = 'gray')   
            plt.scatter(a,b, s = 30, c = 'b')   
            if save:
                plt.savefig('./img/tfg_test/circ_center.png', bbox_inches='tight', pad_inches=0)
            plt.show()


        return a,b 


