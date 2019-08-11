# Geographical Clustering via k-Medoids Algorithm

This repository offers a solution for sorting streets or coordinates into clusters using Google Maps' API via the k-medoids algorithm.

### Table of Contents
- [Warning](#Warning)
- [Algorithm](#Algorithm)
- [Requirements](#Requirements)
- [Usage](#Usage-of-this-code)
- [Problems and Limitations](#Problems-and-Limitations)
- [Results](#Results)

## Warning!

**USING THIS CODE CAN CAUSE HIGH COSTS! PROCEED WITH CAUTION!**

If a valid Google API key is given, this code will send requests to Google Maps' Distance Matrix API in order to fill the distance matrix.
Unfortunately, the number of needed requests scales with the squared amount of data points.
In detail, if `n` is the number of streets to be clustered, `0.5 * n * (n+1) - n` requests will be sent to the Distance Matrix API.
Assuming one requests costs 0.005 EUR, for `n=100` this will cause costs totaling to approximately 25 EUR.
Because of the quadratic scaling, clustering 10000 elements will cost two hundred fifty thousand Euros!

**DISCLAIMER** *The programmer of this project takes no liability for any resulting costs! The user has been warned that high cost may emerge and he is highly advised to make appropriate settings in the API's account to prevent unexpected billing!*

## Algorithm

This project clusters addresses using the k-medoids algorithm described by [Park and Jun (2009) Expert Syst. Appl. 36.](https://www.researchgate.net/publication/220215167_A_simple_and_fast_algorithm_for_K-medoids_clustering)
The code follows the structure and nomenclature of that paper. Thus, comments marking the single steps of the algorithm can be found throughout the code.
It was chosen to use the k-medoids algorithm, since an arbitrary metric can be used with this algorithm.

In this case, the arbitrary metric is the time it takes to drive from one point to the other by car.
The usage of this metric was carefully chosen, since it was implemented for trying to solve the positioning problem for parcel hubs.
If one wishes to change the means of travel or to switch to another metric, the code will provide explanations on how to achieve those changes.
## Requirements
 - python 3 is used for this project, since python 2.7 has some trouble saving German umlauts as entries in its list
 - numpy library is used
 - googlemaps library is used. It can be installed via pip by `pip3 install -U googlemaps`
 - For serious usage a Google Maps API key is needed, which can be generated [here](https://cloud.google.com/maps-platform/). Even if only the demo version is being used, getting an API key is highly recommended for being able to use the plotting functionality.

## Usage of this code

This repository offers two solutions.
Firstly, a standalone solution, which consist of a single file.
That file can be imported to other projects and it offers a fairly simple usage.
Secondly, the other solution offers the same functionality, however it serves a different purpose.
Its purpose is to visualise the results and functioning as a demonstration, therefore being able to use precalculated datasets and play with the clustering algorithm.

In order to find the correct street in the correct city, it is advised to add the city name to the street name.

### Standalone File
The standalone solution is saved in 'geo_k_medoids.py' and it is meant to be used as an import file for easy usage as shown in the following.
```python
import geo_k_medoids

list_of_streets = ['Jagdhornstr. 16 München', 'Ulrichsbergstr. 13 München', 'Ampfingstr. 2 München', 'Kurzmannweg 24 München', 'Jacobistr. 19 München', 'Eisgruberstr. 23 München', 'Friedrich-Herschel-Str. 22 München', 'Hans-Heiling-Str. 25 München', 'Platz der Menschenrechte 25 München']

result_list = geo_k_medoids.geo_k_medoids(  api_key="your valid Google API key here",
                                            list_of_streets=list_of_streets,
                                            k=3 )
```
Printing the `result_list` returns the following list, where each entry represents a cluster and each of those clusters is saved as a dictionary.
```python
[{'center': 'Jacobistr. 19 München', 'members': ['Kurzmannweg 24 München', 'Jacobistr. 19 München', 'Friedrich-Herschel-Str. 22 München', 'Hans-Heiling-Str. 25 München', 'Platz der Menschenrechte 25 München']}, {'center': 'Ulrichsbergstr. 13 München', 'members': ['Ulrichsbergstr. 13 München', 'Ampfingstr. 2 München']}, {'center': 'Jagdhornstr. 16 München', 'members': ['Jagdhornstr. 16 München', 'Eisgruberstr. 23 München']}]
```
### Demo Version
The code for the demo version can be found in the 'src' directory and consists of three files: the actual demo, a file containing all classes, and a file containing auxiliary functions - split for the sake of readability.\
The best usage of this demonstration can be obtained by using the code in an IDE of your choice.
Since the calculation of the distance matrix is monetarily expensive (see [Problems and Limitations](#Problems-and-Limitations)), precalculated datasets can be used in the demo version:
Four demo datasets are available with 30, 70, 100, or 150 random addresses in Munich respectively.
If one wishes to use them, the dataset's name must simply be passed (munich_<number_of_addresses>) as an argument for the demo keyword in the geo_k_medoids_demo() function.
That way the expensive part will be skipped.
Even though no valid API key is needed for the computation, a valid key is needed for being able to create plots of the result as shown in results.
So, it is advised to use such a key.\
The only part a user has to deal with, is the function call of geo_k_medoids_demo():
```python
if __name__ == "__main__":

    geo_k_medoids_demo(k=3,
                       api_key="your valid Google API key here",
                       list_of_streets="",
                       demo="munich_150",
                       plot=True)
 ```
 Running this will create the results shown in results.
 
 ## Problems and Limitations
 - As mentioned [before](#Warning) calculating the distance matrix is monetarily expensive, the total cost explodes for high number of data points. For example, clustering ten thousand streets will cost a quarter million Euros, which is absolutely insane.
 - This implementation is also timely expensive. In total `0.5 * n * (n+1) - n` requests for `n` data points have to be made, and assuming one request takes about 30ms, running this algorithm for a thousand streets will take at least 4 hours.
 - Another limitation that the demo version has, is the number of plottable points on a map. According to Google Developer's Guide, the maximum length of an URL request is 8192 characters. So, after a certain amount of data points it will not be possible to plot them on a map.
 - Lastly, the demo version is focused on plotting addresses in Munich, so the URL is centralised in Munich. If one wants to plot addresses out of Munich, the function responsible for plotting will have to be modified. Alternatively, a logic can be built which automatically sets the center and zoom level for the Google Static Map API request.
 ## Results
 These are the results of this algorithm, whereby the following pictures were created by the demo version of this project.
 As mentioned before, a valid Google API key is needed for the production of the links for those pictures.
 
 The following two pictures show the results for the 'munich_150' dataset.
 The fist picture simply shows the 150 random addresses in Munich.
 <p float="center">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_150/munich150_k7_step0.png" width="400">
 </p>
 
 The following three pictures show the upper addresses spilt into three, seven, and twelve clusters (from left to right respectively).

 <p float="center">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_150/munich150_k3_step4_final.png" width="270">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_150/munich150_k7_step3_final.png" width="270">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_150/munich150_k12_step5_final.png" width="270">
 </p>
 
 Further images can be found in the demo directory.
 ### Short Analysis of Results
 A short analysis can be done with the demo data. By plotting the total cost against the number of clusters, as done in the following picture, it can be seen that the optimal amount of clusters is at around twelve.
 Significantly increasing the number of clusters, will not effectively reduce the total cost.
 Obviously, by assuming fifty clusters the total cost will reduce, however no use case can be thought of so far in which it would make sense to cluster 150 addresses into fifty clusters.
 <p float="center">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/plot_number_k.png" width="400">
 </p>
 
 ### Illustration of the Algorithm
 As eyecandy, the following gif illustrates how the algorithm clusters different streets.
 Both animations show the clustering into twelve clusters, whereby the left animation shows the process for the munich_70 dataset and the right animation for the munich_150 dataset.
  <p float="center">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_70/munich70_k12_animation.gif" width="400">
  <img src="https://github.com/dprosperino/geographical-k-medoids-clustering/blob/master/demo/munich_150/munich150_k12_animation.gif" width="400">
 </p>
