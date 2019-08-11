import sys
import numpy as np


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


def get_nearest_center(street, list_clusters, distance_matrix):
    """ Takes an address and returns the cluster it has the smallest distance to.

    :param address:         type Address, of which the nearest cluster is searched for
    :param list_clusters:   list of clusters, elements are of type Cluster
    :param distance_matrix: distance matrix coding the distance from each point to each point
    :return:                type Cluster from which address, has the smallest distance to
    """
    list_distances = list()

    for cluster in list_clusters:
        list_distances.append(distance_matrix[street.get_iid(), cluster.get_center().get_iid()])

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


def clean_street_name(string_street_name):
    string_street_name = string_street_name.replace("ä", "ae")
    string_street_name = string_street_name.replace("ö", "oe")
    string_street_name = string_street_name.replace("ü", "ue")
    string_street_name = string_street_name.replace("ß", "ss")
    string_street_name = string_street_name.replace(" ","")

    return string_street_name


def plot_cluster_string(cluster, label_cluster_center, color):
    """ This function returns a string containing all the necessary information for a Google Static Map API request for
        one cluster! Hence it prints a request string for one cluster.

    :param cluster:                 type Cluster to be worked with
    :param label_cluster_center:    string of label of the center of the cluster
    :param color:                   color of that cluster in hexadecimal notation starting with an 0x
    :return:                        string containing information of one cluster, which can be added to Google Static Map
                                    API request
    """
    marker_string = ""

    # Add center
    marker_string += "&markers=color:{}|label:{}|{}".format(color, label_cluster_center, cluster.get_center().get_geo_location())

    # Add members of cluster
    marker_string += "&markers=color:{}|size:small".format(color)
    for street in cluster.get_member():
        marker_string += "|{}".format(clean_street_name(street.get_geo_location()))

    return marker_string


def plot_streets(cluster):
    """ This function takes a cluster and returns all coordinates of members of this cluster without any label
        information

    :param cluster: type Cluster, which is going to be analised
    :return:        returns string containing all coordinates of members of given class without any label information,
                    ready to be added to a Google Static Map API request
    """
    marker_string = ""

    for street in cluster.get_member():
        marker_string += "|{}".format(clean_street_name(street.get_geo_location()))

    return marker_string


def wait_user_assertion(amount_expected_requests):
    """ As discussed, using too many Distance Matrix API requests can get really expensive real quick. This is why,
        we wait for the user's assertion, so the user does not get surprised by the price.

    :param amount_expected_requests:    integer stating the amount of expected Google Maps' Distance Matrix API requests
    """
    print("WARNING!\tYou are going to perform {} requests to Google Maps' Distance Matrix API."
          .format(amount_expected_requests))
    print("\t\t\tThe account belonging to this API key will be charged with approximately {}€, if you choose to continue."
        .format(round(0.005 * amount_expected_requests, 2)))
    print("\nDo you wish to continue?")
    user = input("Enter yes or no: ")
    if user == "yes" or user == "y":
        print("Starting calculation of distance matrix.\nThis step may take some time.")
    else:
        sys.exit("Process aborted by user's choice.")
				

def list_of_colors(number_colors_needed):
		# The seven standard colors, which have been chosen manually
    colors = ["0xfc0303", "0x98fc03", "0x03e3fc", "0x3903fc", "0xdf03fc", "0xff9900", "0xff00bf"]

    if number_colors_needed > 7:
        amount_increment = int(16777215/number_colors_needed-7)	# 16777215 is the amount of possible RGB colors

        color = 0
        for i in range(number_colors_needed-7):
            color += (amount_increment * (i+1))
            colors.append(str(hex(color)))

    return colors
		