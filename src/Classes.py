import string
import googlemaps

import util as u


class GoogleMapsClient:

    def __init__(self, api_key):
        self.__api_key = api_key
        self.__gmaps_client = googlemaps.Client(key = api_key)

    def distance_between_streets(self, street_one, street_two):
        """ This function uses the Google Distance Matrix API for its queries. In this context, distance means the time
            in seconds it takes to drive from street one to street two. If one wishes to use the driving distance, the
            keyword "duration" has to be changed to "distance". If one wishes to use a different mean of transportation,
            it should be specified as an extra argument in the distance matrix function.
            See https://developers.google.com/maps/documentation/distance-matrix/intro#optional-parameters
            (last called on 08.08.2019) for further information.

        :param street_one:  string of street name or coordinates of first street
        :param street_two:  string of street name of coordinates of second street
        :return:            distance between two given streets, note the different meaning of distance here!
        """
        return self.__gmaps_client.distance_matrix(street_one, street_two)['rows'][0]['elements'][0]['duration']['value']

    def address_to_coordinates(self, street_name):
        """ Since the Google Maps' Static Map API does not allow more then fifteen human readable addresses in their
            links, the addresses have to be converted into a not human readable form, hence coordinates.

        :param street_name: string of street name the coordinates are asked for
        :return:            string of latitude and longitude of street name using Google Maps Geocode API
        """
        coordinates_dict = self.__gmaps_client.geocode(street_name)[0]["geometry"]["location"]
        return "{},{}".format(coordinates_dict["lat"], coordinates_dict["lng"])

    def plot_history(self, history_dict):
        """ This function takes a history dictionary, in which the key is the time step and the value is the list of
            clusters at that time step. It then returns a list of URLs for each time step.

        :param history_dict:    dictionary where key is time step and value is list of clusters at that time step
        :return:                list of valid URLs for Google's Static Maps API
        """

        list_of_urls = list()

        list_of_colors = u.list_of_colors(len(history_dict[0])) # len(history_dict[0]) is number of clusters
        list_of_labels = [str(char) for char in string.ascii_uppercase]

        for time_step in range(len(history_dict)):
            marker_string = ""

            # TODO: Center is hardcoded to Munich. Select automated center, eventually.
            beginning_url = "https://maps.googleapis.com/maps/api/staticmap?center=Munich,Germany&zoom=11&size=600x600&maptype=roadmap"
            marker_string = beginning_url

            list_of_clusters = history_dict[time_step]

            for i, cluster in enumerate(list_of_clusters):
                marker_string += u.plot_cluster_string(cluster, list_of_labels[i], list_of_colors[i])

            marker_string += "&key={}".format(self.__api_key)
            list_of_urls.append(marker_string)

        return list_of_urls

    def plot_streets_without_label(self, history_dict):
        """ This function plots all streets but does not plot any cluster information. This is basically the initial
            state.

        :param history_dict:    dictionary where key is time step and value is list of clusters at that time step
        :return:                URL for Google's Static Map API with all points on that map
        """

        beginning_url = "https://maps.googleapis.com/maps/api/staticmap?center=Munich,Germany&zoom=11&size=600x600&maptype=roadmap"
        marker_string = beginning_url
        marker_string += "&markers=color:{}|size:small".format("0xa5a8ad")  # neutral greyish color

        clusters = history_dict[0]

        for cluster in clusters:
            marker_string += u.plot_streets(cluster)

        marker_string += "&key={}".format(self.__api_key)
        return marker_string


class Address:

    def __init__(self, iid, street_name, cluster=None):
        self._iid = iid             # since id is a key word in python
        self._name = street_name
        self._cluster = cluster
        self._v = 0                 # see Hae-Sang Park and Chi-Hyuck Jun, 2009 in Expert Syst. Appl. 36.
        self._geo_location = ""

    def __str__(self):
        return self._name

    def set_cluster(self, cluster):
        self._cluster = cluster

    def get_cluster(self):
        return self._cluster

    def set_iid(self, iid):
        self._iid = iid

    def get_iid(self):
        return self._iid

    def set_v(self, v):
        self._v = v

    def get_v(self):
        return self._v

    def set_geo_location(self, coordinates):
        self._geo_location = str(coordinates)

    def get_geo_location(self):
        return self._geo_location

    def get_street_name(self):
        return self._name


class Cluster:

    def __init__(self, center):
        self._center = center
        self._members = list()

    def __str__(self):
        return "The center of this cluster is {} and its members are {}" \
            .format(str(self._center), [street.get_street_name() for street in self._members])

    def set_center(self, new_center):
        self._center = new_center

    def get_center(self):
        return self._center

    def get_member(self):
        return self._members

    def add_member(self, address):
        """ This function adds a new address to this cluster. Simultaneously, it deletes the passed address in its old
            cluster. Thus, we secure, that each address has only one single cluster.

        :param address: type Address, which should be added to this cluster. Deletes this entry from old cluster!
        """
        old_cluster = address.get_cluster()
        old_cluster.delete_member(address)
        address.set_cluster(self)
        self._members.append(address)

    def delete_member(self, address):
        """ Deletes passed address of type Address from this cluster.

        :param address: type Address, which is going to be deleted
        """
        if str(address) in [str(ad) for ad in self._members]:
            self._members.remove(address)
        # Possible problems: Same address twice!
        # TODO: Deal with duplicate addresses!

    def set_minimising_center(self, distance_matrix):
        """ This function gets the medoid of this cluster and sets it as the new center

        :param distance_matrix: matrix containing all distances between every data points
        """
        list_of_costs = list()

        for address in self._members:
            self.set_center(address)
            list_of_costs.append(u.calculate_cost(self._members, distance_matrix))

        minimising_index = list_of_costs.index(min(list_of_costs))

        self.set_center(self._members[minimising_index])

    def set_geo_location_for_members(self, gmaps):
        """ This function sets the attribute geo_location for each of its members. It needs an instance of
            GoogleMapsClient for calling the coordinates of a given address

        :param gmaps:   instance of GoogleMapsClient being able to use the Geolocation API
        """
        for street in self._members:
            street.set_geo_location( gmaps.address_to_coordinates(street.get_street_name()) )
