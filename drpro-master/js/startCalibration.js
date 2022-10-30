
import { doc, updateDoc } from "firebase/firestore";

const washingtonRef = doc(db, "cities", "DC");

// Set the "capital" field of the city 'DC'
$( "#calibration" ).on( "click", async function () {
    doc(db, "Settings", "settings").get()
    await updateDoc(washingtonRef, {
        mode: "Calibration"
    });
})