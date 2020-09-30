import numpy as np 
import copy
import random
from math import e
import statistics
import json
import os.path
from os import path
import argparse
import warnings

import cv2
from PIL import Image
from matplotlib import cm
import concurrent.futures

import dot_series



def progress(value, max=100):
    return HTML("""
        <progress
            value='{value}'
            max='{max}',
            style='width: 100%'
        >
            {value}
        </progress>
    """.format(value=value, max=max))

def average_color(img):
	flat_img = img.flatten()
	return (np.average(flat_img[0::3]), np.average(flat_img[1::3]), np.average(flat_img[2::3]))

def calculate_error(difference):
	return np.sum(difference)

def plot_dots(img2, main_dots):
	img = np.copy(img2)
	if len(main_dots) > 0:
		for i, curr_dot in enumerate(main_dots):
			cv2.circle(img, tuple(map(int, curr_dot.position[::-1])), curr_dot.radius, tuple(map(int, curr_dot.color)), -1)
	return img

def gray_img(diff):
	return cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

def find_winner(choices, dot, main_dots, beg, blank):
	errors = []
	all_options = []
	for e, curr_dot in enumerate(choices):
		temp_dots = copy.deepcopy(main_dots)
		if curr_dot.infront:
			temp_dots.append(curr_dot)
		else:
			temp_dots.insert(0, curr_dot)
		all_options.append(temp_dots)
		
	with concurrent.futures.ThreadPoolExecutor() as executor:
		#print(str(all_options) + "BB")
		
		
		
		results = [executor.submit(score_dots, option, beg, blank) for option in all_options]
		
		for result in results:
			err = result.result()
			errors.append(err)
	
		#errors.append(calculate_error(cv2.absdiff(beg, plot_dots(blank, temp_dots))))
		
	
	winner_index = np.argsort(errors)
	#print(winner_index)
	#print(all_options)
	win_dot = choices[winner_index[0]]
	return win_dot, winner_index[0]

def score_dots(temp_dots, beg, blank):
	return calculate_error(cv2.absdiff(beg, plot_dots(blank, temp_dots)))


class ToDot:
	def __init__(self, my_path, look_path, final_path, starting_img = "",
		number_of_dots = 1000, blur_amount = 17, diff_blur_amount = 17):
		
		self.number_of_dots = number_of_dots
		self.blur_amount = blur_amount
		self.diff_blur_amount = diff_blur_amount
		self.my_path = my_path
		self.look_path = my_path + look_path
		self.final_path = my_path + final_path
		self.starting_img = starting_img
		#self.my_path = "C:\\Users\\Andrew\\Desktop\\Python Stuff\\projects\\calculated Dots\\"

	
	def start(self):
		#Open the image and blur it a little
		beg = cv2.imread(self.look_path)
		#print(self.look_path)
		beg = cv2.GaussianBlur(beg,(self.blur_amount,self.blur_amount),0)

		avg_color = average_color(beg)

		warnings.simplefilter(action='ignore', category=FutureWarning)
		if self.starting_img == "":
			blank = np.zeros((beg.shape[0],beg.shape[1],beg.shape[2]),np.uint8)
			cv2.rectangle(blank, (0, 0), (beg.shape[1], beg.shape[0]), avg_color, -1)
		else:
			blank = self.starting_img

		#cv2.imwrite(my_path + "poo.png", blank)

		main_dots = []

		for i in range(self.number_of_dots):
			progress(i, max=self.number_of_dots)
			difference = cv2.absdiff(beg, blank)
			
			if self.diff_blur_amount > 0:
				difference = cv2.GaussianBlur(difference,(self.diff_blur_amount,self.diff_blur_amount),0)
			
			(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray_img(difference))
			pos = (beg[maxLoc[1], maxLoc[0]])
			b,g,r = pos
			dot = dot_series.Dot((maxLoc[1], maxLoc[0]), 1, (b, g, r))
			
			changer = 0
			inactive_count = 0
			while inactive_count < 10:
				if changer == 0:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot)]
					choises[1].radius += 1
					choises[1].radius += 5
					choises[2].radius += 10
					choises[3].radius = max(choises[2].radius - 1, 1)
					choises[4].radius = max(choises[2].radius - 5, 1)
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
					
				elif changer == 1:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot)]
					choises[1].color = (min(choises[1].color[0] + 5, 255), choises[1].color[1], choises[1].color[2])
					choises[1].color = (min(choises[1].color[0] + 1, 255), choises[1].color[1], choises[1].color[2])
					choises[1].color = (max(choises[1].color[0] - 5, 0), choises[1].color[1], choises[1].color[2])
					choises[1].color = (max(choises[1].color[0] - 1, 0), choises[1].color[1], choises[1].color[2])
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
				elif changer == 2:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot)]
					choises[1].color = (choises[1].color[0], min(choises[1].color[1] + 5, 255), choises[1].color[2])
					choises[1].color = (choises[1].color[0], min(choises[1].color[1] + 1, 255), choises[1].color[2])
					choises[1].color = (choises[1].color[0], max(choises[1].color[1] - 5, 0), choises[1].color[2])
					choises[1].color = (choises[1].color[0], max(choises[1].color[1] - 1, 0), choises[1].color[2])
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
				elif changer == 3:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot)]
					choises[1].color = (choises[1].color[0], choises[1].color[1], min(choises[1].color[2] + 5, 255))
					choises[1].color = (choises[1].color[0], choises[1].color[1], min(choises[1].color[2] + 1, 255))
					choises[1].color = (choises[1].color[0], choises[1].color[1], max(choises[1].color[2] - 5, 0))
					choises[1].color = (choises[1].color[0], choises[1].color[1], max(choises[1].color[2] - 1, 0))
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
				elif changer == 4:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot),  copy.deepcopy(dot),
								copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot),  copy.deepcopy(dot),
								copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot),  copy.deepcopy(dot),
								copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot),  copy.deepcopy(dot)]
					choises[1].position = (choises[1].position[0] + 1, choises[1].position[1])
					choises[2].position = (choises[2].position[0] - 1, choises[2].position[1])
					choises[3].position = (choises[3].position[0], choises[3].position[1] + 1)
					choises[4].position = (choises[4].position[0], choises[4].position[1] - 1)
					choises[5].position = (choises[1].position[0] + 5, choises[1].position[1])
					choises[6].position = (choises[2].position[0] - 5, choises[2].position[1])
					choises[7].position = (choises[3].position[0], choises[3].position[1] + 5)
					choises[8].position = (choises[4].position[0], choises[4].position[1] - 5)
					
					choises[9].position = (choises[1].position[0] + 1, choises[1].position[1] + 1)
					choises[10].position = (choises[2].position[0] - 1, choises[2].position[1] + 1)
					choises[11].position = (choises[3].position[0] + 1, choises[3].position[1] - 1)
					choises[12].position = (choises[4].position[0] - 1, choises[4].position[1] - 1)
					choises[13].position = (choises[1].position[0] + 5, choises[1].position[1] + 5)
					choises[14].position = (choises[2].position[0] - 5, choises[2].position[1] + 5)
					choises[15].position = (choises[3].position[0] + 5, choises[3].position[1] - 5)
					choises[16].position = (choises[4].position[0] - 5, choises[4].position[1] - 5)
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
				else:
					choises = [copy.deepcopy(dot), copy.deepcopy(dot), copy.deepcopy(dot)]
					choises[1].infront = True
					choises[2].infront = False
					
					dot, winner = find_winner(choises, dot, main_dots, beg, blank)
					if winner == 0:
						inactive_count += 1
					else:
						inactive_count = 0
				
				
				changer += 1
				if changer == 6:
					changer = 0
			if dot.infront:
				main_dots.append(dot)
			else:
				main_dots.insert(0, dot)
			
			blank = plot_dots(blank, main_dots)
			#difference = cv2.absdiff(beg, blank)
			cv2.imwrite(self.final_path, blank)
			"""
			print(main_dots[0].position)
			print(main_dots[0].radius)
			print(main_dots[0].color)
			
			cv2.imshow("beg", beg)
			cv2.imshow("blank", blank)
			cv2.imshow("diff", difference)
			
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			"""
			
			#plot_dots(img, main_dots)

		progress(self.number_of_dots, max=self.number_of_dots)
		print("")
		return blank
