import googlemaps
import numpy as np



################################################ DEFINITIONS OF CLASSES ################################################

class GoogleMapsClient:

    def __init__(self, api_key):
        self.__gmaps_client = googlemaps.Client(key=api_key)

    def distance_between_streets(self, street_one, street_two, metric):
        """ This function uses the Google Distance Matrix API for getting the distance between to streets.
            Note the following points!

            -   The developer has to chose what 'distance' means by choosing the correct metric. If a time metric
            is chosen, the distance is the travelling time in seconds using a car. If the distance metric is chosen,
            the result will be the driving distance by car in meters(?) between those to points.

            -   Without any further specification, the following scenario describes travelling by car. However, the
            developer can use different means of transportation by adding those as an argument in the distance_matrix
            function. See https://developers.google.com/maps/documentation/distance-matrix/intro#optional-parameters
            (site last called on 08.08.2019)

        :param street_one:  string of first street
        :param street_two:  string of second street
        :param metric:      string specifying usage of certain metric. "time" for travelling time and "distance" for
                            travelling distance
        :return:            distance between street_one and street_two calculated by Google's Distance Matrix API
        """
        assert(metric == "time" or metric == "distance"), "Unvalid metric has been chosen, try 'time' or 'distance'"
        query = ("duration" if metric == "time" else metric)
        return self.__gmaps_client.distance_matrix(street_one, street_two)['rows'][0]['elements'][0][query]['value']


class Address:

    def __init__(self, iid, street_name, cluster=None):
        self._iid = iid         # since id is a key word in python
        self._name = street_name
        self._cluster = cluster
        self._v = 0             # see Hae-Sang Park and Chi-Hyuck Jun, 2009 in Expert Syst. Appl. 36.

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

    def get_street_name(self):
        return self._name


class Cluster:

    def __init__(self, center):
        self._center = center
        self._members = list()

    def __str__(self):
        return "center of cluster is {} and its members are {}"\
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
        """ This function gets the mediod of this cluster and sets it as the new center

        :param distance_matrix: matrix containing all distances between every data points
        """
        list_of_costs = list()

        for address in self._members:
            self.set_center(address)
            list_of_costs.append(calculate_cost(self._members, distance_matrix))

        minimising_index = list_of_costs.index(min(list_of_costs))

        self.set_center(self._members[minimising_index])



#################################################### AUXILIARY PART ####################################################


def sum_over_columns(matrix, row):
    result = 0
    for i in range(len(matrix)):
        result += matrix[row, i]

    return result


def calculate_v(index, matrix):
    """ See Hae-Sang Park and Chi-Hyuck Jun, 2009  in Expert Syst. Appl. 36. for calculation of v!

    :param index:   index of entry to be considered
    :param matrix:  ndarray distance matrix
    :return:        returns v according to paper
    """
    result = 0
    for i in range(len(matrix)):
        divisor = sum_over_columns(matrix, row=i)
        result += matrix[i, index] / divisor

    return result


def symmetrise(matrix):
    return matrix + matrix.T - np.diag(matrix.diagonal())


def get_nearest_center(address, list_clusters, distance_matrix):
    """ Takes an address and returns the cluster it has the smallest distance to.

    :param address:         type Address, of which the nearest cluster is searched for
    :param list_clusters:   list of clusters, elements are of type Cluster
    :param distance_matrix: distance matrix coding the distance from each point to each point
    :return:                type Cluster from which address, has the smallest distance to
    """
    list_distances = list()

    for cluster in list_clusters:
        list_distances.append(distance_matrix[address.get_iid(), cluster.get_center().get_iid()])

    return list_distances.index(min(list_distances))


def assign_street_cluster(streets, list_clusters, distance_matrix):
    """ This function assigns an address to a cluster. Not to any cluster, but to the nearest cluster! It has no
        return value, since it works directly with the instances.

    :param streets:         type Address which is going to be assigned to nearest cluster
    :param list_clusters:   list of clusters, elements are of type Cluster
    :param distance_matrix: distance matrix coding the distance from each point to each point
    """
    for street in streets:
        index_nearest_center = get_nearest_center(street, list_clusters, distance_matrix)
        list_clusters[index_nearest_center].add_member(street)


def calculate_cost(data, distance_matrix):
    """ Calculates the cost, hence the sum of all distances from each street to the cluster they belong to

    :param data:            list of addresses, elements are of type Address
    :param distance_matrix: distance matrix coding the distance from each point to each point
    :return:                sum of all distances from each street to the cluster they belong to
    """
    cost = 0
    for street in data:
        cost += distance_matrix[street.get_iid(), street.get_cluster().get_center().get_iid()]

    return cost


################################################## MAIN FUNCTIONALITY ##################################################


def geo_k_medoids(api_key, list_of_streets, k, metric="time"):
    """ This function clusters a given list of streets (or coordinates) using the k-medoids algorithm described in:
        Hae-Sang Park and Chi-Hyuck Jun, 2009, A simple and fast algorithm for K-medoids clustering, in
        Expert Syst. Appl. 36. 3336-3341.
        The steps are according to upper mentioned paper.
        In this implementation the metric is defined as Google Maps' travel time by car. If one wishes, the driving
        distance can also be selected by changing the metric accordingly.

    :param api_key:         string of Google Services API key, for being able to use their services
    :param list_of_streets: list containing strings, which represents the data one wishes to cluster
    :param k:               integer showing the number of clusters
    :param metric:          "time" for travel time by car between points and "distance" for travel distance by car
                            Nb. If one wishes, the car feature can be changed by looking into class GoogleMapsClient
    :return:                list of dictionaries, in which each dictionary represents one cluster as indicated in the
                            following: {"center": "street1", "members":["street 1", "street 2"]}
    """

    assert(len(list_of_streets)<500),"By proceeding, high costs will encounter! " \
                                     "The account belonging to passed API key will be charged with at least {} EUR! " \
                                     "Delete this assertion, only if you know what you are doing! "\
                                    .format(str(0.0025*len(list_of_streets)**2 + 0.0025*len(list_of_streets)))

    # Initialisation
    gmaps = GoogleMapsClient(api_key)

    init_street = Address(iid=-1, street_name='init')
    init = Cluster(center=init_street) # cluster to which all addresses will be initialised

    distance_matrix = np.zeros((len(list_of_streets), len(list_of_streets)), dtype=int)

    data = list()
    for i, street in enumerate(list_of_streets):
        data.append(Address(iid=i, street_name=street, cluster=init))

    # Filling entries of distance matrix
    for column in range(len(data)):
        for row in range(column):
            distance_matrix[column, row] = gmaps.distance_between_streets(street_one=data[column].get_street_name(),
                                                                          street_two=data[row].get_street_name(),
                                                                          metric=metric)

    distance_matrix = symmetrise(distance_matrix)

    # STEP 1-2
    for i in range(len(data)):
        data[i].set_v(calculate_v(i, distance_matrix))

    v_list = np.array([data[i].get_v() for i in range(len(data))])

    # STEP 1-3
    indices_initial_mediods = v_list.argsort()[:k]

    list_clusters = list()
    for index in indices_initial_mediods:
        list_clusters.append(Cluster(center=data[index]))

    # STEP 1-4
    assign_street_cluster(streets=data, list_clusters=list_clusters, distance_matrix=distance_matrix)

    # STEP 1-5
    cost = calculate_cost(data, distance_matrix)
    
    # STEP 2 and 3
    while True:
        for cluster in list_clusters:
            cluster.set_minimising_center(distance_matrix)

        assign_street_cluster(streets=data, list_clusters=list_clusters, distance_matrix=distance_matrix)

        if calculate_cost(data, distance_matrix) >= cost:
            break

        cost = calculate_cost(data, distance_matrix)

    result = list()
    for cluster in list_clusters:
        result.append({"center":cluster.get_center().get_street_name(),
                       "members":[street.get_street_name() for street in cluster.get_member()]})

    return result
