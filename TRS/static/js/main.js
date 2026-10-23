function searchBuses() {
    const source =
        document.getElementById("source").value.trim();

    const destination =
        document.getElementById("destination").value.trim();

    const travelDate =
        document.getElementById("travel_date").value;

    if (!source || !destination || !travelDate) {
        alert("Please enter From, To and Travel Date.");
        return;
    }

    console.log("Source:", source);
    console.log("Destination:", destination);
    console.log("Date:", travelDate);

    const searchUrl =
        `/search/?from=${encodeURIComponent(source)}&to=${encodeURIComponent(destination)}&date=${encodeURIComponent(travelDate)}`;

    window.location.href = searchUrl;
}