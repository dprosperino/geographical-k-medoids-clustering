import sys
import copy as copy
import numpy as np
import pickle as p

import Classes as c
import util as u


def geo_k_medoids_demo(k, api_key="", list_of_streets="", demo="", plot=True):
    """ This is the visual demonstration for the geo_k_medoids function in the geo_k_medoids.py module. This function
        follows the exact same algorithm, namely the one described by Hae-Sang Park and Chi-Hyuck Jun, 2009,
        A simple and fast algorithm for K-medoids clustering, in Expert Syst. Appl. 36. 3336-3341.

        This function, however, takes a few more arguments, since it is meant to be a stand alone program. The additional
        arguments are "demo" and "plot".

        Unfortunately, a distance matrix is needed for this calculation. Since the number of entries for this matrix
        grows with n squared, it is monetary expensive to calculate this distance matrix: Approximately 55€ for
        eleven thousand requests, which correspond to 150 addresses. No one wants to pay that much money for a neat trick
        or visualisation. That is why, I precalculated some datasets with its corresponding distance matrix, for you
        to play around with this algorithm.
        Till now, there are four datasets available with 30, 70, 100 and 150 random addresses each. They can be found
        in the demo directory. If you want to use one of those datasets, you will have to type the name of the folder
        in the demo argument.

        Sadly, for being able to see the plots, you still need a Google API key. However, creating the maps is monetary
        neglectable.

        If the demo parameter is empty, you will have the full functionality of the k-medoids algorithm.
        Beware of the costs!

    :param k:               number of clusters one wishes to split the addresses into
    :param api_key:         string of Google Services API key, for being able to use their services
    :param list_of_streets: list containing strings, which represents the data one wishes to cluster
    :param demo:            Choose "munich_30", "munich_70", "munich_100", or "munich_150" for using precalculated
                            datasets
    :param plot:            True, if links to Google's Static Map API should be generated.
                            Attention! If True, costs will incure for converting street names to GPS coordinates and
                            if you click on the generated links for using Static Maps API!
    """

    # Initialisation
    init_street = c.Address(iid=-1, street_name='init')
    init = c.Cluster(center=init_street)

    if api_key:
        gmaps = c.GoogleMapsClient(api_key)

    if demo:
        print("Starting demo version, dataset {} selected".format(demo))

        # Loading demo files
        try:
            file_street_list = open("../demo/{}/{}_street_list.obj".format(demo, demo), "rb")
            list_of_streets = p.load(file_street_list)
            file_street_list.close()

            # STEP 1-1
            file_distance_matrix = open("../demo/{}/{}_distance_matrix.obj".format(demo, demo), "rb")
            distance_matrix = p.load(file_distance_matrix)
            file_distance_matrix.close()

        except FileNotFoundError:
            sys.exit("No files found in demo/{} directory.".format(demo))

        data = list()
        for i, street in enumerate(list_of_streets):
            data.append(c.Address(iid=i, street_name=street, cluster=init))

    else:
        # No demonstration! Actual usage of algorithm

        assert (api_key != ""), "No Google API key given, cannot send requests."
        assert (list_of_streets != ""), "No list of streets given, try demo version."

        data = list()
        for i, street in enumerate(list_of_streets):
            data.append(c.Address(iid=i, street_name=street, cluster=init))

        # STEP 1-1
        distance_matrix = np.zeros((len(data), len(data)), dtype=int)

        amounts_request = int(0.5 * len(data) * (len(data) + 1) - len(data))
        u.wait_user_assertion(amounts_request)

        for column in range(len(data)):
            for row in range(column):
                distance_matrix[column, row] = gmaps.distance_between_streets(street_one=data[column].get_street_name(),
                                                                              street_two=data[row].get_street_name())

        distance_matrix = u.symmetrise(distance_matrix)

    # STEP 1-2
    for i in range(len(data)):
        data[i].set_v(u.calculate_v(i, distance_matrix))

    v_list = np.array([data[i].get_v() for i in range(len(data))])

    # STEP 1-3
    indices_initial_mediods = v_list.argsort()[:k]

    list_clusters = list()
    for index in indices_initial_mediods:
        list_clusters.append(c.Cluster(center=data[index]))

    # STEP 1-4
    u.assign_street_cluster(streets=data, list_clusters=list_clusters, distance_matrix=distance_matrix)

    # STEP 1-5
    cost = u.calculate_cost(data, distance_matrix)

    # STEP 2
    n = 0
    history_dict = dict()

    if api_key:
        # Since Google Maps' Static Map API allows only a maximum of fifteen human readable addresses, all addresses
        # need to be converted to GPS coordinates, again using Google's API and spending even more money...
        for cluster in list_clusters:
            cluster.set_geo_location_for_members(gmaps)

    while True:
        history_dict[n] = copy.deepcopy(list_clusters)

        for cluster in list_clusters:
            cluster.set_minimising_center(distance_matrix)

        u.assign_street_cluster(streets=data, list_clusters=list_clusters, distance_matrix=distance_matrix)
        n += 1

        if u.calculate_cost(data, distance_matrix) >= cost:
            break

        cost = u.calculate_cost(data, distance_matrix)

    # Printing reslults
    print("\nResults!")

    if plot and not api_key:
        print("A valid Google API key is needed for the plots.")

    if api_key and plot:

        print("Printing links to plots")
        print("Step 0: {}".format(gmaps.plot_streets_without_label(history_dict)))

        list_urls = gmaps.plot_history(history_dict)

        for i, entry in enumerate(list_urls):
            print("Step {}: {}".format(i+1, entry))

    print("\nCost of optimised clustering into {} clusters: {} seconds\n".format(k, cost))

    for cluster in list_clusters:
        print(cluster)


if __name__ == "__main__":

    geo_k_medoids_demo(k=3,
                       api_key="",
                       list_of_streets="",
                       demo="munich_100",
                       plot=True)