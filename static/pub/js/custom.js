$(function() {
	// Mobile Button
	$('#MobileNavButton a').click(function() {
		$('#MobileNavWrapper').slideToggle('slow');
	});
	
	// Right align dropdowns
	var $NavItems = $('header nav > *').not('.CustomerLogin').not('.SocialIcons');
	for (var i=0; i<$NavItems.length; i++) {
		var $CurItem = $($NavItems[i]);
		if (i >= $NavItems.length / 2 && $CurItem.hasClass('HasChildren'))
			$CurItem.addClass('Right');
	}
	
	// Mobile Nav Handling
	$('.HasChildren > a').click(function(e) {
		e.preventDefault();
		var $Sublevel = $(this).closest('.HasChildren').find('.Sublevel');
		if (!$Sublevel.hasClass('Expanded')) {
			$Sublevel.slideDown('fast', function() {
				$Sublevel.addClass('Expanded');
				$Sublevel.css('display', '');
			});
		}
	});
	
	// Jukebox Button
	if ($('#JukeboxPlayer').length) {
		$Jukebox = $('#JukeboxPlayer');
		$HideJukebox = $('#HideJukebox');
		$('.Jukebox').click(function() {
			$Jukebox.prop('volume', 1.0).fadeIn('slow');
			$HideJukebox.fadeIn('slow');
			$('#oggSource').attr('src', '/Background/' + $(this).attr('data-sample') + '.wav');
			$('#mp3Source').attr('src', '/Background/' + $(this).attr('data-sample') + '.mp3');
			$Jukebox.load();
			$Jukebox.trigger('play');
		});
		$HideJukebox.click(function(e) {
			e.preventDefault();
			$('#oggSource').attr('src', '');
			$('#mp3Source').attr('src', '');
			$Jukebox.fadeOut(10, function() {
				$Jukebox.animate({volume: 0.0}, 1, function() {
					$Jukebox.trigger('pause');
				});
			});
			$HideJukebox.fadeOut('slow');
		});
	}
	
	// Samples Select
	if ($('#SampleSelectForm').length) {
		var $Jukebox = $('#JukeboxPlayer'),
			$HideJukebox = $('#HideJukebox'),
			$JukeboxRow = $Jukebox.parent();
		$('> div', '#SamplesWrapper').each(function() {
			var $SampleID = $(this).attr('id').replace('Samples', '');
			var $SampleOption = $('option[value=' + $SampleID + ']');
			$(this).prepend('<h1>' + $SampleOption.html() + '</h1>');
			$SampleOption.html($SampleOption.html() + ' (' + $(this).find('> input.Jukebox').length + ')');
		});
		$('select', '#SampleSelectForm').change(function() {
			$('> div', '#SamplesWrapper').css('display', '');
			$Jukebox.hide();
			$HideJukebox.hide();
			var category = $(this).find(':selected').val();
			$('div[id=' + category + 'Samples]').fadeIn('slow').append($JukeboxRow);
		});
	}
	
	// Career Select
	if ($('#CareerLinks').length) {
		$('.Career').first().parent().append('<div class="Hidden"></div>');
		$('a', '#CareerLinks').click(function(e) {
			e.preventDefault();
			var id = $(this).attr('href').substr(1);
			$('a', '#CareerLinks').removeClass('Current');
			$(this).addClass('Current');
			if (id === 'Show-All') {
				$('.Career').each(function(){
					$('.Hidden').before($(this));
				});
			}
			else {
				$('.Career').each(function(){
					$('.Hidden').append($(this));
				});
				$('#' + id).each(function() {
					$('.Hidden').before($(this));
				});
			}
		});
	}
	
	// FAQ Select
	if ($('#FAQWrapper').length) {
		$('.FAQ').not('[data-group="' + $('.FAQ-Button.Button-Info').attr('href').substring(1) + '"]').hide();
		$('.FAQ-Button').click(function(e) {
			if (!$(this).hasClass('Button-Info')) {
				$('.FAQ').hide();
				$('.FAQ[data-group="' + $(this).attr('href').substring(1) + '"]').fadeIn('slow');
				$('.FAQ-Button').removeClass('Button-Info').addClass('Button-Default');
				$(this).removeClass('Button-Default').addClass('Button-Info');
			}
		});
	}
	
	// Backend Groups
	if ($('.Group').length) {
		var canToggleGroup = true;
		
		$('.Group > a').click(function() {
			var $groupItems = $(this).siblings('.GroupItems');
			if (canToggleGroup) {
				canToggleGroup = false;
				if ($groupItems.is(':visible')) $(this).removeClass('Active');
				else $(this).addClass('Active');
				$(this).siblings('.GroupItems').slideToggle('fast',function() {
					canToggleGroup = true;
				});
			}
		});
	}
	
	// Contact Form Scripts
	var SecurityNumber = 0;
	if ($('.SecurityCheck').length) {
		function RandomizeSecurity() {
			var Val1 = Math.floor(Math.random() * (9)) + 1;
			var Val2 = Math.floor(Math.random() * (9)) + 1;
			SecurityNumber = Val1 + Val2;
			$('.SecurityCheckText').html(Val1 + ' + ' + Val2 + ' = ');
			if ($('.SecurityCheck').val().trim() === (SecurityNumber + '')) {
				console.log('Generating a value was ' + SecurityNumber + ', generating a new one')
				RandomizeSecurity();
			}
		}
		RandomizeSecurity();
	}
	if ($('.Page','form').length) {
		var $Pages = [];
		var $Form = $('form');
		var $AllPages = $('.Page','form');
		var $PrevButton = $('.PageBtn.Previous');
		var $NextButton = $('.PageBtn.Next');
		var $SubmitButton = $('input[type="submit"]');
		
		$AllPages.each(function() { $Pages.push($(this)); });
		var CurPage = 0;
		$AllPages.hide();
		$Pages[CurPage].show();
		$PrevButton.hide();
		$SubmitButton.hide();
		
		$NextButton.click(function() {
			console.log($Form[0].checkValidity());
			if ($Form[0].checkValidity()) {
				CurPage++;
				if (CurPage === $Pages.length - 1) {
					$NextButton.hide();
					$SubmitButton.show();
				}
				if (CurPage !== 0)
					$PrevButton.show();
				$AllPages.hide();
				$Pages[CurPage].show();
				window.scrollTo(0,0);
			}
			else $Form.find(':submit').click();
		});
		$PrevButton.click(function() {
			console.log($Form[0].checkValidity());
			if ($Form[0].checkValidity()) {
				CurPage--;
				if (CurPage === 0)
					$PrevButton.hide();
				if (CurPage !== $Pages.length - 1) {
					$NextButton.show();
					$SubmitButton.hide();
				}
				$AllPages.hide();
				$Pages[CurPage].show();
				window.scrollTo(0,0);
			}
			else $Form.find(':submit').click();
		});
	}
	
	/*$('#ContactForm').submit(function(e) {
        var $ActiveForm = $(this);
		e.preventDefault();
		var Passes = true;
		if ($('.SecurityCheck').length) {
			$('.SecurityError').remove();
			if ($('.SecurityCheck').val().trim() !== (SecurityNumber + '')) {
				$ActiveForm.append('<label class="SecurityError" style="display: none;">Security answer incorrect, the question has been changed.</label>');
				$('.SecurityError').fadeIn('slow');
				RandomizeSecurity();
				Passes = false;
			}
		}
		if (Passes) {
            $(':submit').attr('disabled', 'disabled');
            $.ajax({
                type: "POST",
                url: "Actions/MailHandler.cfm",
                data: $(this).serialize(),
                dataType: "text",
                success: function(data, status) {
                    console.log(status);
		            $ActiveForm.slideUp('slow', function () {
		                $ActiveForm.parent().append('<h3>Your message has been sent!  We will be in touch shortly.</h3>');
		            });
                }
            });
		}
	});*/
	
	// Jukebox Button
	if ($('#JukeboxShufflePlayer').length) {
		$Jukebox = $('#JukeboxShufflePlayer');
		$HideJukebox = $('#HideJukebox');
		$('.JukeboxSh').click(function() {
			$Jukebox.prop('volume', 1.0).fadeIn('slow');
			$HideJukebox.fadeIn('slow');
			$('#oggSource').attr('src', '/Waves/' + $(this).attr('data-sample') + '.wav');
			$('#mp3Source').attr('src', '/MP3s/' + $(this).attr('data-sample') + '.mp3');
			$Jukebox.load();
			$Jukebox.trigger('play');
		});
		$HideJukebox.click(function(e) {
			e.preventDefault();
			$('#oggSource').attr('src', '');
			$('#mp3Source').attr('src', '');
			$Jukebox.fadeOut(10, function() {
				$Jukebox.animate({volume: 0.0}, 1, function() {
					$Jukebox.trigger('pause');
				});
			});
			$HideJukebox.fadeOut('slow');
		});
	}
	
	// SHUFFLE MUSIC Jukebox Button
	if ($('#JukeboxShuffleMusicPlayer').length) {
		$Jukebox = $('#JukeboxShufflePlayer');
		$HideJukebox = $('#HideJukebox');
		$('.JukeboxShMus').click(function() {
			$Jukebox.prop('volume', 1.0).fadeIn('slow');
			$HideJukebox.fadeIn('slow');
			$('#oggSource').attr('src', '/Background/' + $(this).attr('data-sample') + '.wav');
			$('#mp3Source').attr('src', '/Background/' + $(this).attr('data-sample') + '.mp3');
			$Jukebox.load();
			$Jukebox.trigger('play');
		});
		$HideJukebox.click(function(e) {
			e.preventDefault();
			$('#oggSource').attr('src', '');
			$('#mp3Source').attr('src', '');
			$Jukebox.fadeOut(10, function() {
				$Jukebox.animate({volume: 0.0}, 0, function() {
					$Jukebox.trigger('pause');
				});
			});
			$HideJukebox.fadeOut('slow');
		});
	}
	
	
	if($('.MyJukeboxPlayer').length) {
		var backAudio = $('.MyJukeboxPlayer');
	
		var muted = false;
		
		$('.PauseButton').click(function(){
			var button = $(this);
			if (!muted) {
				button.attr("disabled", "");
				backAudio.animate({volume: 0}, 1, function () {
					muted = true;
				});
			}
			else {
				button.attr("disabled", "");
				backAudio.animate({volume: 1}, 1, function () {
					muted = false;
				});
			}
		});
	}
	
	// GENERATE PRODS CLICK DC
	$("#GenerateButton").click(function() {
        /*$("#ShuffleDetails").trigger('submit');*/
		$("#ShuffleDetails").submit();
		return false;
	});
	
	// DATED SCRIPTS UPDATE DC
	$("#DatedFormButton").click(function() {
		$("#DatedForm").submit();
		return false;
	});
	
	$("#bCopy1").click(function() {
		$("#fcpall").submit();
		return false;
	});
	
	// CUSTOM SCRIPTS TABS
	// 6/6/2016 DC
	$("#cstabs").tabs();
	
	$(".Dates").datepicker({
		dateFormat: "m/d/yy",
		minDate: 0
	});
	
	// PLAY PAUSE TOGGLE
    // 7/8/2016 DC
	$(".PlayButton").click(function () {
        var thisId = $(this).data("sample");
        console.debug(thisId);
		/*if (window.HTMLAudioElement) {
                try {
                    var oAudio = document.getElementById('JukeboxShufflePlayer');
                    //var btn = document.getElementById('play'); 
                    var audioURL = $(this).data("sample") + ".mp3"; 

                    //Skip loading if current file hasn't changed.
                    if (audioURL.value !== currentFile) {
                        oAudio.src = audioURL.value;
                        currentFile = audioURL.value;                       
                    }

                    // Tests the paused attribute and set state. 
                    if (oAudio.paused) {
                        oAudio.play();
                        //btn.textContent = "Pause";
                    }
                    else {
                        oAudio.pause();
                        //btn.textContent = "Play";
                    }
                }
                catch (e) {
                    // Fail silently but show in F12 developer tools console
                     if(window.console && console.error("Error:" + e));
                }
            }
        }*/
    	$("#PlayPause"+thisId).toggleClass("fa-play fa-stop");
		$("#JukeboxPlay"+thisId).toggleClass("PlayButton PauseButton");
		
		$(".PauseButton").click(function() {
			$("audio").trigger("pause");
			
		});
		
		$(".PlayButton").click(function() {
			$("audio").trigger("play");
			
		});
	});
	
	$("#ClearGroups").click(function() {
		$("#ClearDlg").html( "Are you sure you want to clear all groups?");
		$("#ClearDlg").dialog({
			resizable: false,
			height: "auto",
			width: 400,
			modal: true,
			buttons: {
				"Clear all groups": function() {
				  $( this ).dialog( "close" );
				},
				Cancel: function() {
				  $( this ).dialog( "close" );
				}
			}
		});
	});
	
	// CONTENT CHANGE FLAG DIALOG - ON DASHBOARD PAGE IF URL.FLAG EQ 1
	$("#dlg").dialog({
		modal: true,
		closeOnEscape: true,
		resizable: false,
		position: ['center' ],
		height: "auto",
		width: 400,
		buttons: {
			"Ok": function() {
				$(this).dialog("close");
				$.cookie("OhmgShuffleChange", 1, {
				   	expires : 1,
				    path    : '/',
				   	domain  : 'main.onholdwizard.com',
					secure  : true         
				});
			  	
			}
		}
	});
	
	// PW4 SELECT SCRIPT FUNCTIONALITY DC 10/27/2017
	/*$(".SelCheckBox").click(function() {
		var myValue = $(this).attr('id');
		$.cookie("PWLIST", myValue, { expires: 10 });
	});*/
	$(".AddRegion").click(function() {
        $("#dialog-confirm").text("Do you want to add all locations from this region?");
        $( "#dialog-confirm" ).dialog({
              html: "",
              resizable: false,
              height: "auto",
              width: 400,
              modal: true,
              buttons: {
                "Yes": function() {
                  location.href="";
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                }
              }
            });
        });
    

        $("#ClearScripts").click(function() {
            $("#dialog-confirm").text("Do you want to clear all scripts from this group?");
            $( "#dialog-confirm" ).dialog({
              html: "",
              resizable: false,
              height: "auto",
              width: 400,
              modal: true,
              buttons: {
                "Yes": function() {
                  $("#fClearScripts").submit();
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                }
              }
            });
        });
    
        $("#ClearMusic").click(function() {
            $("#dialog-confirm").text("Do you want to clear all music tracks from this group?");
            $( "#dialog-confirm" ).dialog({
              html: "",
              resizable: false,
              height: "auto",
              width: 400,
              modal: true,
              buttons: {
                "Yes": function() {
                  $("#fClearMusic").submit();
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                }
              }
            });
        });
    
        $(".AddRegion").click(function() {
            var thisId = $(this).data("regid");
            $("#dialog-confirm").text("Do you want to add all locations from this region?");
            $( "#dialog-confirm" ).dialog({
              html: "",
              resizable: false,
              height: "auto",
              width: 400,
              modal: true,
              buttons: {
                "Yes": function() {
                  $("#fAddRegion"+thisId).submit();
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                }
              }
            });
        });

});

