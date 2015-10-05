# -*- coding: utf-8; -*-
#
# This file contains an implementation of a generalised Kendall tau distance for partial rankings.
# The implementation follows the description in section 3.1 of the following article:
#
# Fagin, Ronald, et al. "Comparing and aggregating rankings with ties."
# Proceedings of the twenty-third ACM SIGMOD-SIGACT-SIGART symposium on Principles of database systems. ACM, 2004.
#

def rankingToBucketOrder(ranking):
    """
    :param ranking: A partial ranking defined as a list of tuples. The first element of the tuple is the item in
    the ranking, while the second element is the position of the element in the ranking. No ordering is assumed in
    the ranking.
    Example of partial ranking: [('a',1),('b',2),('c',1),('d',3),('e',2)]
    :return: A bucket order.
    """
    maxPosition = max([position for (item,position) in ranking])
    print "Max position:",maxPosition
    bucketOrder = [set() for i in range(maxPosition)]
    print "BucketOrder = ",bucketOrder
    for (item,position) in ranking:
        bucketOrder[position - 1].add(item)
    print "BucketOrder = ",bucketOrder
    return bucketOrder

def getBucketPosition(bucket,bucketOrder):
    if bucket in bucketOrder:
        bucketIndex = bucketOrder.index(bucket)
        total = (len(bucket) + 1) / 2.0
        for i in range(0,bucketIndex):
            total += len(bucketOrder[i])
        return total
    else:
        return -1

def getBucket(item,bucketOrder):
    for bucket in bucketOrder:
        if item in bucket:
            return bucket
    return set([])

def getItemPosition(item,bucketOrder):
    bucket = getBucket(item,bucketOrder)
    return getBucketPosition(bucket,bucketOrder)

def getPairs(domain):
    return [(x, y) for x in domain for y in domain if x != y and domain.index(x) < domain.index(y)]

def inSameBucket(i,j,bucketOrder):
    if getItemPosition(i,bucketOrder) == getItemPosition(j,bucketOrder):
        return True
    else:
        return False

def inSameOrder(i,j,bucketOrder1,bucketOrder2):
    iPositionInOrder1 = getItemPosition(i,bucketOrder1)
    jPositionInOrder1 = getItemPosition(j,bucketOrder1)
    iPositionInOrder2 = getItemPosition(i,bucketOrder2)
    jPositionInOrder2 = getItemPosition(j,bucketOrder2)
    return (iPositionInOrder1 > jPositionInOrder1 and iPositionInOrder2 > jPositionInOrder2) or (iPositionInOrder1 < jPositionInOrder1 and iPositionInOrder2 < jPositionInOrder2)

def kendallPairDistance(i,j,p,bucketOrder1,bucketOrder2):
    if not(inSameBucket(i,j,bucketOrder1)) and not(inSameBucket(i,j,bucketOrder2)):
        if inSameOrder(i,j,bucketOrder1,bucketOrder2):
            return 0
        else:
            return 1
    elif inSameBucket(i,j,bucketOrder1) and inSameBucket(i,j,bucketOrder2):
        return 0
    elif (inSameBucket(i,j,bucketOrder1) and not(inSameBucket(i,j,bucketOrder2))) or (not(inSameBucket(i,j,bucketOrder1)) and inSameBucket(i,j,bucketOrder2)):
        return p

def kendallDistance(p,domain,bucketOrder1,bucketOrder2):
    """
    This function computes the generalised Kendall tau distance for partial rankings
    :param p: penalty parameter
    :param domain: domain of the values ranked
    :param bucketOrder1: bucket order defining a partial ranking
    :param bucketOrder2: bucket order defining a partial ranking
    :return: Kendall tau distance
    """
    total = 0
    for (i,j) in getPairs(domain):
        total += kendallPairDistance(i,j,p,bucketOrder1,bucketOrder2)
    return total


if __name__ == "__main__":

    #
    # Examples
    #

    domain = ['a','b','c','d','e']

    bucketOrder1 = []
    bucketOrder2 = []
    bucketOrder3 = []
    bucketOrder4 = []
    bucketOrder5 = []
    bucketOrder6 = []

    bucket1 = set(['a', 'b'])
    bucket2 = set(['c'])
    bucket3 = set(['d','e'])

    bucket4 = set(['a'])
    bucket5 = set(['d','e'])
    bucket6 = set(['b','c'])

    bucket7 = set(['d','e'])
    bucket8 = set(['b','c'])
    bucket9 = set(['a'])

    bucket10 = set(['a'])
    bucket11 = set(['b'])
    bucket12 = set(['c'])
    bucket13 = set(['d'])
    bucket14 = set(['e'])


    bucketOrder1.append(bucket1)
    bucketOrder1.append(bucket2)
    bucketOrder1.append(bucket3)

    bucketOrder2.append(bucket4)
    bucketOrder2.append(bucket5)
    bucketOrder2.append(bucket6)

    bucketOrder3.append(bucket1)
    bucketOrder3.append(bucket2)
    bucketOrder3.append(bucket3)

    bucketOrder4.append(bucket7)
    bucketOrder4.append(bucket8)
    bucketOrder4.append(bucket9)

    bucketOrder5.append(bucket10)
    bucketOrder5.append(bucket11)
    bucketOrder5.append(bucket12)
    bucketOrder5.append(bucket13)
    bucketOrder5.append(bucket14)

    bucketOrder6.append(bucket12)
    bucketOrder6.append(bucket13)
    bucketOrder6.append(bucket10)
    bucketOrder6.append(bucket11)
    bucketOrder6.append(bucket14)


    # Test the generalised kendall distance for partial rankings

    print kendallDistance(0.5,domain,bucketOrder1,bucketOrder2)
    print kendallDistance(0.5,domain,bucketOrder1,bucketOrder3)
    print kendallDistance(0.5,domain,bucketOrder1,bucketOrder4)

    # Test the Kentall distance for "full" rankings (Wikipedia example)
    print kendallDistance(0.5,domain,bucketOrder5,bucketOrder6)

    # Using the ranking to bucket order function
    a = [('a',1),('b',2),('c',1),('d',3),('e',2)]
    b = [('a',2),('b',3),('c',3),('d',3),('e',1)]
    aBucketOrder = rankingToBucketOrder(a)
    bBucketOrder = rankingToBucketOrder(b)
    print kendallDistance(0.5,domain,aBucketOrder,bBucketOrder)