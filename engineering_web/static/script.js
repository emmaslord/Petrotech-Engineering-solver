
const testButton = document.getElementById("testButton");
const testMessage = document.getElementById("testMessage");

testButton.addEventListener("click", function () {
    testMessage.textContent =
        "JavaScript is working! Your solver frontend is connected.";
});
