import numpy as np
import const
import heapq

# Define what to do when one or both opinions are undefined

def calculateSimilarity(x,y,d):
    return 0 if (x == np.inf or y == np.inf) else (1 - abs(x-y)/float(d))
   # return np.inf if (x == np.inf or y == np.inf) else abs(x-y)/float(d)


def calculateSimilarities(opinions,metaOpinions,domainSize):

    # Create similarity matrix as a 3-D array
    reviewers = opinions.shape[0]
    reviews = opinions.shape[1]
    similarity = np.zeros((reviewers,reviewers,reviews))
    for (i,j,p),value in np.ndenumerate(metaOpinions):
        if value == np.inf:
            # if o_i has no opinion about o_j's review for paper p, compute direct similarities between reviews
            s = calculateSimilarity(opinions[i,p],opinions[j,p],domainSize)
        else:
            # otherwise use the meta-opinion (normalised to be within [0..1])
            s = value /domainSize
        similarity[i,j,p] = s
    return similarity


def getPapersInCommon(opinions,i,j):
    commonReviews = opinions[i] + opinions[j]
    papersMask = (commonReviews != np.inf)
    arePapersInCommon = np.any(papersMask)
    return arePapersInCommon,papersMask

# The following function computes a trust graph value for two reviewers only if both wrote reviews for at least one common paper.

def initTrustGraph(trustGraph,similarities,opinions):
    for (i,j),value in np.ndenumerate(trustGraph):
        (papersInCommon,papersMask) = getPapersInCommon(opinions,i,j)
        # print (i,j),(papersInCommon,papersMask)
        if papersInCommon:
            trustGraph[i,j] = ((similarities[i,j,:] * papersMask).sum())/(papersMask[papersMask].size)
        else:
            trustGraph[i,j] = np.inf


# The following function builds a dictionary-based version of the trust graph so that the Dijkstra algorithm can operate more efficiently
# Obviously it can be embedded within the initTrustGraph function, but I keep it separate for the moment

def buildDictionaryTrustGraph(trustGraph):
    # Create dictionary to keep the list of edges
    reviewers = trustGraph.shape[0]
    dictTrustGraph = {key: {} for key in range(reviewers)}

    for (i,j),value in np.ndenumerate(trustGraph):
        if value != np.inf and i != j:
            (dictTrustGraph[i])[j] = value

    return dictTrustGraph


def largestValue(graph, start, end):
    """
    This function adapts the Dijkstra algorithm to compute the largest value between two nodes start and end.
    We assume that the distance between two nodes in the graph is some similarity value within [0..1].
    We compute the cost between two given nodes as a product of the distances between the nodes for a path connecting the two nodes.
    This implementation benefits from using a heap (a binary tree) for efficiency purposes.
    Since a push operation inserts the smallest value at the head of the heap, we invert costs when computing a path's cost.
    Instead of maximising cost, we minimise 1/cost, which is equivalent.
    """
    queue = [(1.0, start, [])]
    seen = set()
    while True:
        (cost, node, path) = heapq.heappop(queue)
        if node not in seen:
            path = path + [node]
            seen.add(node)
            if node == end:
                # Print for debugging purposes
                # print "Returning ", 1.0/cost, path
                # There is a sanity check to consider if the total path cost is infinite (it can be removed though)
                pathCost = 1.0/cost if cost!= np.inf else 0
                return pathCost,path
            for (neighbour, neighbourCost) in graph[node].iteritems():
                # Print for debugging purposes
                # print "From ", node, " to ", neighbour,": ", cost * 1.0/neighbour, ", Path: ", path
                # There is a sanity check to consider if neighbourCost is zero (it can be removed though)
                pathCost = cost * 1.0/neighbourCost if cost else np.inf
                heapq.heappush(queue, (pathCost, neighbour, path))


# The following function fills out the trust graph for those reviewers that did not review any paper together

def fillOutTrustGraph(trustGraph,dictTrustGraph):
    for (i,j),value in np.ndenumerate(trustGraph):
        if value == np.inf:
            largestCost, path = largestValue(dictTrustGraph,i,j)
            trustGraph[i,j] = largestCost


if __name__ == "__main__":

    #
    # INITIALISE DATA STRUCTURES
    #
    # Observations about papers
    # x dimension stands for observer
    # y dimension stands for paper

    observations = np.array([[np.inf,np.inf,10],[4,np.inf,5],[7,10,np.inf]])

    # Opinions range from 0 to 10
    # The following constant is employed for normalization purposes

    const.DOMAIN_SIZE = 10

    # Defining example 3-D matrix opinions about opinions

    # Example: No opinions about opinions

    opinionsOpinions = np.array([[[ 10,  10,  10],
            [ np.inf,  np.inf,  np.inf],
            [ np.inf,  np.inf,  np.inf]],
           [[ np.inf, np.inf, np.inf],
            [10, 10, 10],
            [np.inf, np.inf, np.inf]],
           [[np.inf, np.inf, np.inf],
            [np.inf, np.inf, np.inf],
            [10, 10, 10]]])

    # opinionsOpinions = np.array([[[ 10,  10,  10],
    #         [ np.inf,  np.inf,  np.inf],
    #         [ np.inf,  0,  3]],
    #        [[ np.inf, np.inf, 1],
    #         [10, 10, 10],
    #         [4, np.inf, 7]],
    #        [[np.inf, 0, 2],
    #         [6, np.inf, 6],
    #         [10, 10, 10]]])


    # obtaining i's opinions about j regarding all papers

    #print opinionsOpinions[i,j,:]


    # Example to test function longestPath

    # G = {'s':{'u':0.1, 'x':0.5}, 'u':{'v':0.1, 'x':0.2}, 'v':{'y':0.4}, 'x':{'u':0.3, 'v':0.9, 'y':0.2}, 'y':{'s':0.7, 'v':0.6}}

    # print longestPath(G,'s','y')

    # COMPUTE TRUST GRAPH

    # 1. Compute similarity matrix
    similarities = calculateSimilarities(observations,opinionsOpinions,const.DOMAIN_SIZE)
    print "\nSimilarity matrix\n"
    print similarities

    # 2. Initialise trust graph
    reviewers = observations.shape[0]
    trustGraph = np.ones((reviewers,reviewers)) * np.inf
    initTrustGraph(trustGraph,similarities,observations)
    print "\nInitial trust graph:\n"
    print trustGraph

    dictTrustGraph = buildDictionaryTrustGraph(trustGraph)
    print "\nDictionary-based representation of the trust graph:\n"
    print dictTrustGraph

    # 3. Fill out the rest of the trust graph by calling Dijkstra
    fillOutTrustGraph(trustGraph,dictTrustGraph)
    print "\nFinal contents of the trust graph:\n"
    print trustGraph



