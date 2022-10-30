# from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import math

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".\\creds\\neurotechxhackaton-2a3116995da0.json"
import firebase_admin
from firebase_admin import firestore
app = firebase_admin.initialize_app()
db = firestore.client()

collectionName="userHeartRate"
ref = db.collection(collectionName)
query = ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit_to_last(60)

import time
time.sleep(3)
while True:
    docs = query.get()
    time.sleep(60)
    #number of queried samples
    numSamp = 60
    #inicilzation
    avgBPM = 0
    maxBPM = 1
    minBPM = 200

    dataAvg = []
    dataMax = []
    dataMin = []

    #feature definition

    #difnes the number of samples used for feature construction
    measurmentNum = 3
    measurmentCounter = 0
    for doc in docs:
        if measurmentCounter < measurmentNum:
            avgBPM = avgBPM + doc.to_dict()['bpm']
            maxBPM = max(maxBPM, doc.to_dict()['bpm'])
            minBPM = min(minBPM, doc.to_dict()['bpm'])
            measurmentCounter = measurmentCounter + 1
        else:
            dataAvg.append(avgBPM/measurmentNum)
            dataMax.append(maxBPM)
            dataMin.append(minBPM)
            avgBPM = 0
            measurmentCounter = 0



    data = list(zip(dataAvg,dataMin,dataMax))
    print(data)

    #inertias = []

    kmeans = KMeans(n_clusters = 4)
    kmeans.fit(data)

    clusters = kmeans.labels_
    centers = kmeans.cluster_centers_

    d = []
    nthPoint = 0
    averDist = [0, 0, 0, 0]

    for points in data:
        d1 = math.dist(centers[0], points)
        d2 = math.dist(centers[1], points)
        d3 = math.dist(centers[2], points)
        d4 = math.dist(centers[3], points)

        d.append([d1, d2, d3, d4])


        #preleti mean puta 10 = outlier

        potentialOutliersIndex = []
        potentialOutliers = 0

        if potentialOutliers < d[nthPoint][clusters[nthPoint]]:
            potentialOutliers = d[nthPoint][clusters[nthPoint]]
            potentialOutliersIndex.append(nthPoint)

        averDist[clusters[nthPoint]] = averDist[clusters[nthPoint]] + d[nthPoint][clusters[nthPoint]]


        nthPoint = nthPoint + 1


    # Nu = numSamp/measurmentNum


    N = [0, 0, 0, 0]
    for c in clusters:
        N[c] = N[c] + 1

    panic = False
    for i in potentialOutliersIndex:
        # print(averDist[clusters[i]]/N[clusters[i]])
        # print(d[clusters[i]][clusters[i]])
        if averDist[clusters[i]]/N[clusters[i]] * 10 < d[clusters[i]][clusters[i]]:
            panic = True

    print(panic)
#todo iskoristi pandas za bolje formatiranje
#todo isplotuj ovo da vidis sta se desava

# plt.plot(range(1,5), inertias, marker='o')
# plt.title('Elbow method')
# plt.xlabel('Number of clusters')
# plt.ylabel('Inertia')
# plt.show()







