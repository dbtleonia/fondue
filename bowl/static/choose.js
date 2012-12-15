// TODO: Don't use hard-coded literals as indices.
function clickTeam(me) {
    // Toggle this team UI element & save team id
    var teamId
    if (me.className == "selected") {
        me.className = "";
        teamId = "";
    } else {
        me.className = "selected";
        teamId = me.id;
    }
    // Unset the other team
    var team1 = me.parentNode.getElementsByTagName("td")[2];
    var team2 = me.parentNode.getElementsByTagName("td")[3];
    if (me == team1) {
        team2.className = "";
    } else {
        team1.className = "";
    }
    // Save to database
    bowlId = me.parentNode.id
    var xhr = new XMLHttpRequest();
    document.getElementById("status").innerHTML = "Saving..."
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            // TODO: Rollback UI changes on failure.
            document.getElementById("status").innerHTML = xhr.responseText;
        }
    }
    xhr.open("POST", "/player/save", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("bowl=" + escape(bowlId) + "&team=" + escape(teamId))
}
