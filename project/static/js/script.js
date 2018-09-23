$(document).ready(function() {
    debugger;
});

function switch_login_signup(){
	if(document.getElementById("signup").style.display=="none"){
		document.getElementById("login").style.display = "none";
		document.getElementById("signup").style.display = "block";
		document.getElementById("login_signup_text").innerHTML = "Already have an account? <b>Login!</b>";
		document.getElementById("login_signup_title").innerHTML = "Sign up";
	}
	else{
		document.getElementById("login").style.display = "block";
		document.getElementById("signup").style.display = "none";
		document.getElementById("login_signup_text").innerHTML = "Don't have an account? <b>Sign up!</b>";
		document.getElementById("login_signup_title").innerHTML = "Login";
	}
}


function timer(){
	if(document.getElementById("start-stop").innerHTML=="Start"){
		document.getElementById("start-stop").innerHTML="Stop";
		document.getElementById("good_btn").style.display = "none";
		document.getElementById("notgood_btn").style.display = "none";
		var speaker_time = document.getElementById("speaker_time").innerHTML;
		var init_speaker_time = speaker_time
		var secs = speaker_time%60;
		var mins = ((speaker_time/1)-secs)/60;
		if(mins<10){
			mins = '0'+mins;
		}
		if(secs<10){
			secs = '0'+secs;
		}
		document.getElementById("timer").innerHTML = mins+':'+secs
		id = setInterval(countdown, 1000);
		function countdown(){
			if(speaker_time==0){
				clearInterval(id);
				document.getElementById("start-stop").innerHTML="Start";
				document.getElementById("speaker_time").innerHTML = document.getElementById("fixed_speaker_time").innerHTML;
				document.getElementById("good_btn").style.display = "inline";
				document.getElementById("notgood_btn").style.display = "inline";
			}
			else{
				speaker_time = speaker_time-1;
				var secs = speaker_time%60;
				var mins = ((speaker_time/1)-secs)/60;
				if(mins<10){
					mins = '0'+mins;
				}
				if(secs<10){
					secs = '0'+secs;
				}
				document.getElementById("timer").innerHTML = mins+':'+secs;
				document.getElementById("speaker_time").innerHTML = speaker_time;
			}
		}
	}
	else{
		clearInterval(id);
		document.getElementById("start-stop").innerHTML="Start";
	}
}

function reset_timer(){
	clearInterval(id);
	document.getElementById("start-stop").innerHTML="Start";
	document.getElementById("speaker_time").innerHTML = document.getElementById("fixed_speaker_time").innerHTML;
	document.getElementById("timer").innerHTML = "00:00";
}

function lobbying_timer(){
	var speaker_time = document.getElementById("speaker_time").innerHTML;
	var secs = speaker_time%60;
	var mins = ((speaker_time/1)-secs)/60;
	if(mins<10){
		mins = '0'+mins;
	}
	if(secs<10){
		secs = '0'+secs;
	}
	document.getElementById("lobbying_timer").innerHTML = mins+':'+secs
	id = setInterval(countdown, 1000);
	function countdown(){
		if(speaker_time==0){
			window.location.href = document.getElementById("url").innerHTML;
			clearInterval(id);
		}
		else{
			speaker_time = speaker_time-1;
			var secs = speaker_time%60;
			var mins = ((speaker_time/1)-secs)/60;
			if(mins<10){
				mins = '0'+mins;
			}
			if(secs<10){
				secs = '0'+secs;
			}
			document.getElementById("lobbying_timer").innerHTML = mins+':'+secs;
			document.getElementById("speaker_time").innerHTML = speaker_time;
		}
	}
}

function show_account_settings(){
	document.getElementById("settings_modal").style.height = 44+"vh";
	document.getElementById("options").style.display = "none";
	document.getElementById("grading_system_settings").style.display = "none";
	document.getElementById("modal_title").innerHTML = "Account Settings"
	document.getElementById("account_settings").style.display = "block";
}

function show_points_settings(){
	document.getElementById("settings_modal").style.height = 44+"vh";
	document.getElementById("options").style.display = "none";
	document.getElementById("account_settings").style.display = "none";
	document.getElementById("modal_title").innerHTML = "Points System Settings"
	document.getElementById("grading_system_settings").style.display = "block";
}

function show_main(){
	document.getElementById("settings_modal").style.height = 40+"vh";
	document.getElementById("options").style.display = "block";
	document.getElementById("modal_title").innerHTML = "Settings"
	document.getElementById("account_settings").style.display = "none";
	document.getElementById("grading_system_settings").style.display = "none";	
}

function go_back(){
	window.location.href = document.referrer;
}