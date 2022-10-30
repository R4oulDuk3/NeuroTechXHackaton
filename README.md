# NeuroTechXHackaton

## Pipeline
BPM gathered from sensors is read by hearthrate.py script and forwarded to GCP pub/sub. From there heartrateToFirestore.py reads incoming realtime data
and stores it in appropriate firestore collections for future processing.

## Kmeans
We used a KMeans clustering algorithm for our outlier detection using the BPM data.
BPM data is being gathered live and being sent to the database.
In the analysis.py file we are taking 60 seconds of the generated data, which is stored in firestore(the plan is to take longer periods of data collection ~ 10 mins)
After we gather the data we take measurmentNum data points and calculate the minimum, the maximum and the average value(a kind of a moving average raw data processing)

Then we clusterize those 3 features. We calculate the centers of the clusters, and calculate the average distance from each of those points to their respective cluster centers.
We check if the data points distance to the center of the respective cluster centers is ten times bigger
than the average distance of the respective cluster points.

The model was intended to have 2 more breathing belt(BB) features, the breathing rate and the variability of the breathing signal(implemented as two features vmax and vmin)
The calculation of BB features would be done the same way it was done for the BMP features.
