// TODO: Don't use hard-coded literals as indices.
function clickTeam(me, savePath) {
    // Toggle this team UI element & save team id
    var teamId;
    var prevMyClass = me.className;
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
    var otherTeam;
    if (me == team1) {
        otherTeam = team2;
    } else {
        otherTeam = team1;
    }
    var prevOtherClass = otherTeam.className;
    otherTeam.className = "";
    // Save to database
    var bowlId = me.parentNode.id;
    var xhr = new XMLHttpRequest();
    document.getElementById("status").innerHTML = "Saving...";
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            document.getElementById("status").innerHTML = xhr.responseText;
            if (xhr.responseText != "Saved") {
                me.className = prevMyClass;
                otherTeam.className = prevOtherClass;
            }
        }
    }
    xhr.open("POST", savePath, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("bowl=" + escape(bowlId) + "&team=" + escape(teamId));
}
