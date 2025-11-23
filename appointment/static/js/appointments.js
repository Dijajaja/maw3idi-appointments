// Variables globales
let nextAvailableDateSelector;
const body = $(document.body);  // Utiliser jQuery pour body
let nonWorkingDays = [];
let selectedDate = null;
let selectedDateIso = null;
let staffId = null;
let previouslySelectedCell = null;
let isRequestInProgress = false;
let calendar = null;
let initializationAttempts = 0;
const MAX_INITIALIZATION_ATTEMPTS = 5;

// -- Helpers UI --------------------------------------------------------------
function updateSubmitState() {
    const hasSelectedSlot = $('.djangoAppt_appointment-slot.selected').length > 0;
    const hasSelectedDate = !!selectedDateIso;
    
    // Le bouton ne doit être activé QUE si un créneau ET une date sont sélectionnés
    if (hasSelectedSlot && hasSelectedDate) {
        $('.btn-submit-appointment').removeAttr('disabled');
        $('.btn-submit-appointment').prop('disabled', false);
    } else {
        $('.btn-submit-appointment').attr('disabled', 'disabled');
        $('.btn-submit-appointment').prop('disabled', true);
    }
}

// Variables qui seront définies par le template (déclarées seulement si elles n'existent pas déjà)
// Ces variables sont définies dans le template HTML avant ce script
if (typeof rescheduledDate === 'undefined') {
    var rescheduledDate = null;
}
if (typeof timezone === 'undefined') {
    var timezone = 'GMT';
}
if (typeof locale === 'undefined') {
    var locale = 'fr';
}
if (typeof todayBtnText === 'undefined') {
    var todayBtnText = 'Aujourd\'hui';
}
if (typeof previousMonthBtnText === 'undefined') {
    var previousMonthBtnText = 'Mois précédent';
}
if (typeof nextMonthBtnText === 'undefined') {
    var nextMonthBtnText = 'Mois suivant';
}

// Fonction pour initialiser le calendrier
function initializeCalendar() {
    // Limiter le nombre de tentatives
    initializationAttempts++;
    if (initializationAttempts > MAX_INITIALIZATION_ATTEMPTS) {
        console.error('Nombre maximum de tentatives d\'initialisation atteint. Arrêt.');
        return;
    }
    
    // Initialiser les variables jQuery
    nextAvailableDateSelector = $('.djangoAppt_next-available-date');
    
    // Initialiser selectedDate
    selectedDate = (typeof rescheduledDate !== 'undefined' && rescheduledDate) ? rescheduledDate : null;
    
    // Vérifier que FullCalendar est disponible
    if (typeof FullCalendar === 'undefined') {
        console.error('FullCalendar n\'est pas chargé (tentative ' + initializationAttempts + '/' + MAX_INITIALIZATION_ATTEMPTS + ')');
        // Réessayer après un court délai seulement si on n'a pas atteint la limite
        if (initializationAttempts < MAX_INITIALIZATION_ATTEMPTS) {
            setTimeout(initializeCalendar, 500);
        }
        return;
    }
    
    // Vérifier que moment.js est disponible
    if (typeof moment === 'undefined') {
        console.error('Moment.js n\'est pas chargé (tentative ' + initializationAttempts + '/' + MAX_INITIALIZATION_ATTEMPTS + ')');
        // Réessayer après un court délai seulement si on n'a pas atteint la limite
        if (initializationAttempts < MAX_INITIALIZATION_ATTEMPTS) {
            setTimeout(initializeCalendar, 500);
        }
        return;
    }
    
    // Vérifier que l'élément calendrier existe - Essayer plusieurs méthodes
    let calendarEl = document.getElementById('calendar');
    
    // Si pas trouvé avec getElementById, essayer avec jQuery
    if (!calendarEl && typeof $ !== 'undefined') {
        const $calendarEl = $('#calendar');
        if ($calendarEl.length > 0) {
            calendarEl = $calendarEl[0];
            console.log('✓ Calendrier trouvé via jQuery');
        }
    }
    
    // Si toujours pas trouvé, essayer querySelector
    if (!calendarEl) {
        calendarEl = document.querySelector('#calendar');
        if (calendarEl) {
            console.log('✓ Calendrier trouvé via querySelector');
        }
    }
    
    if (!calendarEl) {
        console.error('Élément calendrier introuvable (tentative ' + initializationAttempts + '/' + MAX_INITIALIZATION_ATTEMPTS + ')');
        console.error('Méthodes de recherche utilisées: getElementById, jQuery, querySelector');
        console.error('Éléments avec id="calendar" dans le DOM:', document.querySelectorAll('[id="calendar"]').length);
        console.error('Tous les éléments div:', document.querySelectorAll('div').length);
        
        // Réessayer après un court délai seulement si on n'a pas atteint la limite
        if (initializationAttempts < MAX_INITIALIZATION_ATTEMPTS) {
            setTimeout(initializeCalendar, 500);
        }
        return;
    }
    
    console.log('✓ Élément calendrier trouvé:', calendarEl);
    console.log('Dimensions:', {
        width: calendarEl.offsetWidth,
        height: calendarEl.offsetHeight,
        display: window.getComputedStyle(calendarEl).display,
        visibility: window.getComputedStyle(calendarEl).visibility
    });
    
    // Vérifier si le calendrier est déjà initialisé (valide)
    const hasValidWindowCalendar = !!(window.calendar && typeof window.calendar.render === 'function');
    const hasValidLocalCalendar = !!(calendar && typeof calendar.render === 'function');
    if (hasValidWindowCalendar || hasValidLocalCalendar) {
        console.log('Calendrier déjà initialisé (valide)');
        initializationAttempts = 0; // Réinitialiser le compteur si le calendrier est déjà initialisé
        
        // S'assurer que le calendrier est visible
        const existingCalendarEl = document.getElementById('calendar');
        if (existingCalendarEl) {
            existingCalendarEl.style.display = 'block';
            existingCalendarEl.style.visibility = 'visible';
            existingCalendarEl.style.opacity = '1';
            existingCalendarEl.style.width = '100%';
            existingCalendarEl.style.minHeight = '350px';
        }
        return;
    }
    // Si une variable globale existe mais n'est pas un calendrier valide, la remettre à zéro
    if (window.calendar && typeof window.calendar.render !== 'function') {
        console.warn('Variable window.calendar présente mais invalide. Réinitialisation...');
        try {
            if (typeof window.calendar.destroy === 'function') {
                window.calendar.destroy();
            }
        } catch(_) {}
        window.calendar = null;
    }
    if (calendar && typeof calendar.render !== 'function') {
        calendar = null;
    }
    
    // Initialiser les variables
    staffId = $('#staff_id').val() || null;
    
    // Initialiser le calendrier
    try {
        console.log('Initialisation du calendrier...', {
            calendarEl: calendarEl,
            hasFullCalendar: typeof FullCalendar !== 'undefined',
            hasMoment: typeof moment !== 'undefined'
        });
        
        // S'assurer que calendar est accessible globalement
        window.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            initialDate: selectedDate,
            timeZone: 'GMT',
            locale: (typeof locale !== 'undefined' && locale) ? locale : 'fr',
            headerToolbar: {
                left: 'title',
                right: 'prev,today,next',
            },
            buttonText: {
                today: (typeof todayBtnText !== 'undefined') ? todayBtnText : 'Aujourd\'hui',
            },
            buttonHints: {
                prev: (typeof previousMonthBtnText !== 'undefined') ? previousMonthBtnText : 'Mois précédent',
                next: (typeof nextMonthBtnText !== 'undefined') ? nextMonthBtnText : 'Mois suivant',
            },
            height: '350px',
            aspectRatio: 1.35,
            nowIndicator: true,
            selectable: true,
            dateClick: function (info) {
                const day = info.date.getDay();  // Get the day of the week (0 for Sunday, 6 for Saturday)
                console.log('=== CLIC SUR UNE DATE ===');
                console.log('Date cliquée:', info.dateStr);
                console.log('Jour de la semaine (0=Dimanche, 6=Samedi):', day);
                console.log('Staff ID actuel:', staffId);
                console.log('Jours non travaillés:', nonWorkingDays);
                
                if (nonWorkingDays.includes(day)) {
                    console.log('⚠️ Ce jour est dans la liste des jours non travaillés, ignoré');
                    return;
                }
                
                // Vérifier si un staff member est sélectionné
                if (!staffId || staffId === 'none' || staffId === null || staffId === undefined) {
                    console.error('❌ Aucun staff member sélectionné!');
                    const errorMessageContainer = $('.error-message');
                    errorMessageContainer
                        .empty()
                        .append('<p class="djangoAppt_no-availability-text">' + noStaffMemberSelectedTxt + '</p>')
                        .show();
                    return;
                }

                // If there's a previously selected cell, remove the class
                if (previouslySelectedCell) {
                    previouslySelectedCell.classList.remove('selected-cell');
                }

                // Add the class to the currently clicked cell
                info.dayEl.classList.add('selected-cell');

                // Store the currently clicked cell
                previouslySelectedCell = info.dayEl;

                selectedDate = info.dateStr;
                // Ne PAS définir selectedDateIso ici - il sera défini après la sélection d'un créneau
                // Réinitialiser selectedDateIso pour forcer la sélection d'un créneau
                selectedDateIso = null;
                // Désactiver le bouton car aucun créneau n'est sélectionné
                $('.btn-submit-appointment').attr('disabled', 'disabled');
                $('.btn-submit-appointment').prop('disabled', true);
                console.log('Appel de getAvailableSlots avec date:', info.dateStr, 'et staffId:', staffId);
                getAvailableSlots(info.dateStr, staffId);
                // Mettre à jour l'état du bouton (date choisie mais pas encore de créneau)
                updateSubmitState();
            },
            datesSet: function (info) {
                highlightSelectedDate();
            },
            selectAllow: function (info) {
                const day = info.start.getDay();  // Get the day of the week (0 for Sunday, 6 for Saturday)
                if (nonWorkingDays.includes(day)) {
                    return false;  // Disallow selection for non-working days
                }
                return (info.start >= getDateWithoutTime(new Date()));
            },
            dayCellClassNames: function (info) {
                const day = info.date.getDay();
                if (nonWorkingDays.includes(day)) {
                    return ['disabled-day'];
                }
                return [];
            },
        });
        
        // Forcer les dimensions avant le rendu
        calendarEl.style.width = '100%';
        calendarEl.style.height = '100%';
        calendarEl.style.minHeight = '350px';
        calendarEl.style.display = 'block';
        calendarEl.style.visibility = 'visible';
        calendarEl.style.opacity = '1';
        calendarEl.style.position = 'relative';
        calendarEl.style.overflow = 'visible';
        calendarEl.style.background = 'transparent';
        calendarEl.style.backgroundColor = 'transparent';
        
        // S'assurer que l'élément a des dimensions valides
        if (calendarEl.offsetWidth === 0 || calendarEl.offsetHeight === 0) {
            console.warn('Calendrier a des dimensions nulles, attente...');
            setTimeout(function() {
                calendarEl.style.width = '100%';
                calendarEl.style.height = '100%';
                calendarEl.style.minHeight = '350px';
            }, 100);
        }
        
        // Rendre le calendrier
        console.log('=== TENTATIVE DE RENDU ===');
        console.log('Élément calendarEl:', calendarEl);
        console.log('Dimensions avant rendu:', {
            width: calendarEl.offsetWidth,
            height: calendarEl.offsetHeight,
            computedWidth: window.getComputedStyle(calendarEl).width,
            computedHeight: window.getComputedStyle(calendarEl).height
        });
        console.log('Configuration du calendrier:', {
            initialView: 'dayGridMonth',
            timeZone: 'GMT',
            locale: (typeof locale !== 'undefined' && locale) ? locale : 'fr',
            height: '350px'
        });
        console.log('window.calendar avant render:', window.calendar);
        console.log('Type de window.calendar:', typeof window.calendar);
        
        try {
            console.log('Appel de window.calendar.render()...');
            window.calendar.render();
            calendar = window.calendar; // Garder une référence locale aussi
            console.log('✓ render() appelé avec succès');
            console.log('HTML après rendu (premiers 500 chars):', calendarEl.innerHTML.substring(0, 500));
            console.log('HTML complet length:', calendarEl.innerHTML.length);
            
            // Vérifier que le contenu a été créé
            setTimeout(function() {
                var viewHarness = calendarEl.querySelector('.fc-view-harness');
                if (!viewHarness) {
                    console.error('ERREUR: .fc-view-harness non créé après le rendu!');
                    console.log('HTML du calendrier:', calendarEl.innerHTML);
                    // Vérifier les dimensions
                    console.log('Dimensions de calendarEl:', {
                        width: calendarEl.offsetWidth,
                        height: calendarEl.offsetHeight,
                        display: window.getComputedStyle(calendarEl).display,
                        visibility: window.getComputedStyle(calendarEl).visibility
                    });
                    // Réessayer le rendu seulement si les dimensions sont valides
                    if (calendarEl.offsetWidth > 0 && calendarEl.offsetHeight > 0) {
                        try {
                            if (window.calendar && typeof window.calendar.render === 'function') {
                                window.calendar.render();
                            }
                        } catch(e) {
                            console.error('Erreur lors de la nouvelle tentative de rendu:', e);
                        }
                    } else {
                        console.error('Calendrier a des dimensions nulles, impossible de rendre');
                        // Forcer les dimensions et réessayer
                        calendarEl.style.width = '100%';
                        calendarEl.style.minHeight = '350px';
                        calendarEl.style.height = 'auto';
                        setTimeout(function() {
                            try {
                                if (window.calendar && typeof window.calendar.render === 'function') {
                                    window.calendar.render();
                                }
                            } catch(e) {
                                console.error('Erreur lors de la tentative de rendu après correction des dimensions:', e);
                            }
                        }, 300);
                    }
                } else {
                    console.log('✓ Calendrier correctement rendu avec .fc-view-harness');
                }
            }, 200);
            
            // Forcer le fond blanc après le rendu
            setTimeout(function() {
                calendarEl.style.background = '#ffffff';
                calendarEl.style.backgroundColor = '#ffffff';
                var allChildren = calendarEl.querySelectorAll('*');
                allChildren.forEach(function(el) {
                    if (!el.classList.contains('fc-button') && 
                        !el.classList.contains('fc-event') && 
                        el.tagName !== 'BUTTON' && 
                        !el.closest('.fc-button') &&
                        !el.closest('.fc-event')) {
                        var computedBg = window.getComputedStyle(el).backgroundColor;
                        if (computedBg === 'rgba(0, 0, 0, 0)' || computedBg === 'transparent') {
                            el.style.setProperty('background-color', '#ffffff', 'important');
                        }
                    }
                });
            }, 100);
        } catch (renderError) {
            console.error('Erreur lors du rendu:', renderError);
            console.error('Stack trace:', renderError.stack);
            throw renderError;
        }
        
        // Forcer le rendu après un court délai
        setTimeout(function() {
            var calendarContent = calendarEl.querySelector('.fc-view-harness');
            var fcScrollgrid = calendarEl.querySelector('.fc-scrollgrid');
            var fcHeaderToolbar = calendarEl.querySelector('.fc-header-toolbar');
            
            console.log('=== DIAGNOSTIC APRÈS RENDU ===');
            console.log('fc-view-harness:', calendarContent);
            console.log('fc-scrollgrid:', fcScrollgrid);
            console.log('fc-header-toolbar:', fcHeaderToolbar);
            console.log('HTML complet (premiers 1000 caractères):', calendarEl.innerHTML.substring(0, 1000));
            console.log('Dimensions après rendu:', {
                width: calendarEl.offsetWidth,
                height: calendarEl.offsetHeight,
                scrollWidth: calendarEl.scrollWidth,
                scrollHeight: calendarEl.scrollHeight
            });
            
            if (!calendarContent) {
                console.error('ERREUR: Le contenu du calendrier (.fc-view-harness) n\'a pas été créé!');
                // Ne pas réessayer indéfiniment - seulement si on n'a pas atteint la limite
                if (initializationAttempts < MAX_INITIALIZATION_ATTEMPTS) {
                    console.warn('Nouvelle tentative de rendu...');
                    // Détruire et recréer le calendrier
                    if (window.calendar) {
                        try {
                            window.calendar.destroy();
                        } catch(e) {
                            console.error('Erreur lors de la destruction:', e);
                        }
                        window.calendar = null;
                        calendar = null;
                    }
                    // Réinitialiser
                    setTimeout(initializeCalendar, 500);
                } else {
                    console.error('Nombre maximum de tentatives atteint. Le calendrier ne peut pas être rendu.');
                }
            } else {
                // Réinitialiser le compteur en cas de succès
                initializationAttempts = 0;
                console.log('✓ Calendrier rendu avec succès');
                // Forcer l'affichage et les dimensions
                calendarEl.style.display = 'block';
                calendarEl.style.visibility = 'visible';
                calendarEl.style.opacity = '1';
                calendarEl.style.width = '100%';
                calendarEl.style.height = '100%';
                calendarEl.style.minHeight = '350px';
                
                // Forcer les dimensions des éléments internes
                if (calendarContent) {
                    calendarContent.style.display = 'block';
                    calendarContent.style.height = '300px';
                    calendarContent.style.width = '100%';
                }
                if (fcScrollgrid) {
                    fcScrollgrid.style.display = 'table';
                    fcScrollgrid.style.width = '100%';
                    fcScrollgrid.style.height = '300px';
                }
                
                // S'assurer que le conteneur parent a les bonnes dimensions
                var calendarContainer = calendarEl.closest('.djangoAppt_calendar');
                if (calendarContainer) {
                    calendarContainer.style.display = 'flex';
                    calendarContainer.style.flexDirection = 'column';
                    calendarContainer.style.minHeight = '400px';
                }
            }
        }, 500);
        
        // Obtenir la date actuelle avec le bon timezone
        const currentDate = (typeof rescheduledDate !== 'undefined' && rescheduledDate) 
            ? rescheduledDate 
            : (typeof moment !== 'undefined' 
                ? moment.tz('GMT').format('YYYY-MM-DD') 
                : new Date().toISOString().split('T')[0]);
        
        getAvailableSlots(currentDate, staffId);
        
        console.log('Calendrier initialisé avec succès', calendar);
        // Réinitialiser le compteur en cas de succès
        initializationAttempts = 0;
    } catch (error) {
        console.error('Erreur lors de l\'initialisation du calendrier:', error);
        console.error('Stack trace:', error.stack);
        // Ne pas réessayer indéfiniment
        if (initializationAttempts >= MAX_INITIALIZATION_ATTEMPTS) {
            console.error('Arrêt des tentatives d\'initialisation après ' + MAX_INITIALIZATION_ATTEMPTS + ' tentatives.');
        }
    }
}

// Fonction pour mettre à jour le diagnostic (désactivée - console uniquement)
function updateDiagnostic(key, value, isError) {
    // Diagnostic désactivé - logs dans la console uniquement
    console.log('DIAG [' + key + ']:', value);
}

// Initialiser le calendrier quand le DOM est prêt
$(document).ready(function () {
    console.log('=== $(document).ready EXÉCUTÉ ===');
    console.log('FullCalendar disponible:', typeof FullCalendar !== 'undefined');
    console.log('Moment disponible:', typeof moment !== 'undefined');
    console.log('jQuery disponible:', typeof jQuery !== 'undefined');
    
    // Fonction pour trouver l'élément calendrier avec plusieurs méthodes
    function findCalendarElement() {
        let calendarEl = document.getElementById('calendar');
        
        if (!calendarEl && typeof $ !== 'undefined') {
            const $calendarEl = $('#calendar');
            if ($calendarEl.length > 0) {
                calendarEl = $calendarEl[0];
                console.log('✓ Calendrier trouvé via jQuery');
            }
        }
        
        if (!calendarEl) {
            calendarEl = document.querySelector('#calendar');
            if (calendarEl) {
                console.log('✓ Calendrier trouvé via querySelector');
            }
        }
        
        return calendarEl;
    }
    
    // Vérifier que l'élément calendrier existe
    let calendarEl = findCalendarElement();
    
    if (calendarEl) {
        console.log('✓ Élément #calendar trouvé:', calendarEl);
        console.log('Dimensions initiales:', {
            width: calendarEl.offsetWidth,
            height: calendarEl.offsetHeight,
            display: window.getComputedStyle(calendarEl).display,
            visibility: window.getComputedStyle(calendarEl).visibility
        });
        
        // Si les dimensions sont nulles, attendre un peu et réessayer
        if (calendarEl.offsetWidth === 0 || calendarEl.offsetHeight === 0) {
            console.warn('Calendrier a des dimensions nulles au chargement, attente de 500ms...');
            setTimeout(function() {
                // Forcer les dimensions
                calendarEl.style.width = '100%';
                calendarEl.style.minHeight = '350px';
                calendarEl.style.height = 'auto';
                calendarEl.style.display = 'block';
                calendarEl.style.visibility = 'visible';
                calendarEl.style.opacity = '1';
                // Initialiser le calendrier
                initializeCalendar();
            }, 500);
        } else {
            // Initialiser immédiatement
            initializeCalendar();
        }
    } else {
        console.error('❌ Élément #calendar introuvable dans document.ready!');
        console.error('Nombre d\'éléments avec id="calendar":', document.querySelectorAll('[id="calendar"]').length);
        console.error('Tous les divs:', document.querySelectorAll('div').length);
        
        // Réessayer après un court délai avec plusieurs tentatives
        let retryCount = 0;
        const maxRetries = 10;
        const retryInterval = setInterval(function() {
            retryCount++;
            calendarEl = findCalendarElement();
            
            if (calendarEl) {
                console.log(`✓ Calendrier trouvé après ${retryCount} tentative(s)`);
                clearInterval(retryInterval);
                // Forcer les dimensions avant d'initialiser
                calendarEl.style.width = '100%';
                calendarEl.style.minHeight = '350px';
                calendarEl.style.display = 'block';
                calendarEl.style.visibility = 'visible';
                calendarEl.style.opacity = '1';
                initializeCalendar();
            } else if (retryCount >= maxRetries) {
                console.error(`✗ Élément #calendar toujours introuvable après ${maxRetries} tentatives`);
                clearInterval(retryInterval);
            }
        }, 200);
    }
    
    // Attendre un peu pour s'assurer que tous les scripts sont chargés
    setTimeout(function() {
        console.log('=== TENTATIVE D\'INITIALISATION ===');
        console.log('FullCalendar:', typeof FullCalendar !== 'undefined');
        console.log('Moment:', typeof moment !== 'undefined');
        
        if (typeof FullCalendar !== 'undefined' && typeof moment !== 'undefined') {
            console.log('✓ Toutes les dépendances sont chargées, initialisation...');
            initializeCalendar();
        } else {
            console.error('✗ Dépendances manquantes!');
            console.error('FullCalendar:', typeof FullCalendar);
            console.error('Moment:', typeof moment);
            // Réessayer plusieurs fois
            var retryCount = 0;
            var maxRetries = 10;
            var retryInterval = setInterval(function() {
                retryCount++;
                console.log('Tentative ' + retryCount + '/' + maxRetries + '...');
                if (typeof FullCalendar !== 'undefined' && typeof moment !== 'undefined') {
                    console.log('✓ Dépendances chargées, initialisation...');
                    clearInterval(retryInterval);
                    initializeCalendar();
                } else if (retryCount >= maxRetries) {
                    console.error('✗ ÉCHEC: Dépendances non chargées après ' + maxRetries + ' tentatives');
                    clearInterval(retryInterval);
                }
            }, 500);
        }
    }, 200);
});

// Aussi essayer après le chargement complet de la page
window.addEventListener('load', function() {
    setTimeout(function() {
        if (!window.calendar && !calendar) {
            if (typeof FullCalendar !== 'undefined' && typeof moment !== 'undefined') {
                initializeCalendar();
            } else {
                console.warn('Dépendances non chargées après le chargement de la page');
            }
        }
    }, 500);
});

function highlightSelectedDate() {
    if ((!window.calendar && !calendar) || !selectedDate) return;
    const cal = window.calendar || calendar;
    
    setTimeout(function () {
        const dateCell = document.querySelector(`.fc-daygrid-day[data-date='${selectedDate}']`);
        if (dateCell) {
            dateCell.classList.add('selected-cell');
            previouslySelectedCell = dateCell;
        }
    }, 10);
}

body.on('click', '.djangoAppt_btn-request-next-slot', function () {
    const serviceId = $(this).data('service-id');
    requestNextAvailableSlot(serviceId);
})

body.on('click', '.btn-submit-appointment', function (e) {
    e.preventDefault(); // Empêcher la soumission par défaut
    e.stopPropagation(); // Empêcher la propagation de l'événement
    
    console.log('=== CLIC SUR LE BOUTON SUIVANT ===');
    console.log('Bouton désactivé?', $(this).prop('disabled'));
    console.log('serviceId:', serviceId);
    console.log('selectedDateIso:', selectedDateIso);
    
    // Vérifier si le bouton est désactivé
    if ($(this).prop('disabled')) {
        console.warn('⚠️ Bouton désactivé, mais on continue quand même');
        // Ne pas bloquer, on continue
    }
    
    // Vérifier que le service est défini, mais ne pas bloquer si on peut le récupérer depuis la session
    // Le service sera récupéré depuis la session côté serveur si nécessaire
    if (!serviceId || serviceId === '' || serviceId === 'undefined') {
        console.warn('⚠️ Service ID non défini dans le JavaScript, mais on continue (sera récupéré depuis la session côté serveur)');
        // Ne pas bloquer, on continue quand même
    }
    
    const selectedSlot = $('.djangoAppt_appointment-slot.selected').text();
    const selectedDate = $('.djangoAppt_date_chosen').text();
    console.log('Créneau sélectionné:', selectedSlot);
    console.log('Date sélectionnée:', selectedDate);
    console.log('selectedDateIso:', selectedDateIso);
    console.log('Type de selectedDateIso:', typeof selectedDateIso);
    
    if (!selectedSlot || !selectedDate) {
        console.error('❌ Créneau ou date non sélectionné!');
        console.error('  - selectedSlot:', selectedSlot);
        console.error('  - selectedDate:', selectedDate);
        alert(selectDateAndTimeAlertTxt);
        return false;
    }
    
    // Vérifier que selectedDateIso est défini
    if (!selectedDateIso) {
        console.error('❌ selectedDateIso n\'est pas défini!');
        console.error('Tentative de récupération depuis selectedDate:', selectedDate);
        // Essayer de convertir selectedDate en ISO si possible
        if (selectedDate) {
            // Si selectedDate est au format "DD/MM/YYYY", le convertir en ISO
            const dateMatch = selectedDate.match(/(\d{2})\/(\d{2})\/(\d{4})/);
            if (dateMatch) {
                const [, day, month, year] = dateMatch;
                selectedDateIso = `${year}-${month}-${day}`;
                console.log('✓ selectedDateIso reconstruit depuis selectedDate:', selectedDateIso);
            } else {
                console.error('❌ Impossible de convertir selectedDate en ISO');
                alert('Erreur: Date non valide. Veuillez recharger la page et réessayer.');
                return false;
            }
        } else {
            alert('Erreur: Date non sélectionnée. Veuillez sélectionner une date.');
            return false;
        }
    }

    if (selectedSlot && selectedDateIso) {
        // Extraire l'heure du créneau sélectionné
        let startTime;
        
        // Si le créneau est au format ISO (2025-11-18T09:06:00), extraire l'heure
        if (selectedSlot.includes('T') && selectedSlot.includes(':')) {
            // Format ISO détecté, extraire l'heure
            const isoMatch = selectedSlot.match(/T(\d{2}):(\d{2})/);
            if (isoMatch) {
                const [, hours, minutes] = isoMatch;
                startTime = `${hours}:${minutes}`;
                console.log('Heure extraite du format ISO:', startTime);
            } else {
                // Essayer de parser comme Date
                try {
                    const dateObj = new Date(selectedSlot);
                    if (!isNaN(dateObj.getTime())) {
                        const hours = String(dateObj.getHours()).padStart(2, '0');
                        const minutes = String(dateObj.getMinutes()).padStart(2, '0');
                        startTime = `${hours}:${minutes}`;
                        console.log('Heure extraite depuis Date:', startTime);
                    } else {
                        // Fallback: utiliser convertTo24Hour
                        startTime = convertTo24Hour(selectedSlot);
                    }
                } catch (e) {
                    console.error('Erreur lors de l\'extraction de l\'heure:', e);
                    // Fallback: utiliser convertTo24Hour
                    startTime = convertTo24Hour(selectedSlot);
                }
            }
        } else {
            // Format normal (heure seule), utiliser convertTo24Hour
            startTime = convertTo24Hour(selectedSlot);
        }
        
        const date = selectedDateIso;
        console.log('Heure de début (24h):', startTime);
        console.log('Date (ISO):', date);

        // Calculate end time using ISO date instead of localized date
        const formattedDate = new Date(selectedDateIso + "T" + startTime + ":00");
        const endTimeDate = new Date(formattedDate.getTime() + serviceDuration * 60000);
        const endTime = formatTime(endTimeDate);
        console.log('Heure de fin:', endTime);

        const reasonForRescheduling = $('#reason_for_rescheduling').val();
        const form = $('.appointment-form');
        
        if (form.length === 0) {
            console.error('❌ Formulaire .appointment-form non trouvé!');
            alert('Erreur: Formulaire non trouvé. Veuillez recharger la page.');
            return false;
        }
        
        let formAction = rescheduledDate ? appointmentRescheduleURL : appointmentRequestSubmitURL;
        form.attr('action', formAction);
        
        // Supprimer les anciens champs cachés pour éviter les doublons
        form.find('input[name="date"]').remove();
        form.find('input[name="start_time"]').remove();
        form.find('input[name="end_time"]').remove();
        form.find('input[name="service"]').remove();
        form.find('input[name="reason_for_rescheduling"]').remove();
        
        if (!form.find('input[name="appointment_request_id"]').length) {
            form.append($('<input>', {
                type: 'hidden',
                name: 'appointment_request_id',
                value: appointmentRequestId
            }));
        }
        // Vérifier que les champs essentiels sont définis (date, start_time, end_time)
        if (!date || !startTime || !endTime) {
            console.error('❌ Données manquantes pour la soumission:');
            console.error('  - date:', date);
            console.error('  - start_time:', startTime);
            console.error('  - end_time:', endTime);
            alert('Erreur: Données manquantes. Veuillez recharger la page et réessayer.');
            return false;
        }
        
        // Ajouter les champs au formulaire
        form.append($('<input>', {type: 'hidden', name: 'date', value: date}));
        form.append($('<input>', {type: 'hidden', name: 'start_time', value: startTime}));
        form.append($('<input>', {type: 'hidden', name: 'end_time', value: endTime}));
        
        // Ajouter le service seulement s'il est défini (sinon il sera récupéré depuis la session côté serveur)
        if (serviceId && serviceId !== '' && serviceId !== 'undefined') {
            form.append($('<input>', {type: 'hidden', name: 'service', value: serviceId}));
            console.log('Service ID ajouté au formulaire:', serviceId);
        } else {
            console.warn('⚠️ Service ID non ajouté au formulaire (sera récupéré depuis la session côté serveur)');
        }
        
        form.append($('<input>', {type: 'hidden', name: 'reason_for_rescheduling', value: reasonForRescheduling}));
        
        // Vérifier que les champs ont bien été ajoutés
        const addedDate = form.find('input[name="date"]').val();
        const addedStartTime = form.find('input[name="start_time"]').val();
        const addedService = form.find('input[name="service"]').val();
        
        console.log('Soumission du formulaire avec:');
        console.log('  - date:', date, '(ajouté:', addedDate, ')');
        console.log('  - start_time:', startTime, '(ajouté:', addedStartTime, ')');
        console.log('  - end_time:', endTime);
        console.log('  - service:', serviceId, '(ajouté au formulaire:', addedService || 'sera récupéré depuis la session', ')');
        console.log('  - action:', formAction);
        console.log('  - staff_member:', form.find('select[name="staff_member"]').val());
        
        // Vérifier que tous les champs sont présents avant la soumission
        const allFields = {
            date: form.find('input[name="date"]').val(),
            start_time: form.find('input[name="start_time"]').val(),
            end_time: form.find('input[name="end_time"]').val(),
            service: form.find('input[name="service"]').val(),
            staff_member: form.find('select[name="staff_member"]').val()
        };
        
        console.log('=== VÉRIFICATION FINALE AVANT SOUMISSION ===');
        console.log('Champs dans le formulaire:', allFields);
        
        // Vérifier que les champs essentiels sont présents (service peut être récupéré depuis la session)
        if (!allFields.date || !allFields.start_time || !allFields.end_time || !allFields.staff_member || allFields.staff_member === 'none') {
            console.error('❌ Champs manquants dans le formulaire:', allFields);
            alert('Erreur: Certains champs sont manquants. Veuillez sélectionner un membre du personnel, une date et un créneau.');
            return false;
        }
        
        // Créer un FormData pour vérifier les données
        const formData = new FormData(form[0]);
        console.log('=== DONNÉES DU FORMULAIRE (FormData) ===');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: ${value}`);
        }
        
        // Vérifier que les champs essentiels sont dans FormData (service peut être récupéré depuis la session)
        if (!formData.get('date') || !formData.get('start_time') || !formData.get('end_time')) {
            console.error('❌ Champs essentiels manquants dans FormData!');
            console.error('FormData contient:', Array.from(formData.entries()));
            alert('Erreur: Les champs requis ne sont pas présents dans le formulaire. Veuillez recharger la page.');
            return false;
        }
        
        // Le service peut être récupéré depuis la session côté serveur si absent
        if (!formData.get('service')) {
            console.warn('⚠️ Service non présent dans FormData, sera récupéré depuis la session côté serveur');
        }
        
        console.log('✓ Tous les champs sont présents, soumission du formulaire...');
        console.log('Formulaire trouvé:', form.length > 0);
        console.log('Élément DOM du formulaire:', form[0]);
        console.log('Action du formulaire:', form.attr('action'));
        console.log('Méthode du formulaire:', form.attr('method') || 'POST');
        
        // S'assurer que la méthode est POST
        if (!form.attr('method')) {
            form.attr('method', 'POST');
        }
        
        // Soumettre le formulaire directement - utiliser plusieurs méthodes pour s'assurer que ça fonctionne
        console.log('Tentative de soumission du formulaire...');
        
        // Désactiver le bouton pour éviter les doubles soumissions
        $('.btn-submit-appointment').prop('disabled', true);
        
        // Créer un petit délai pour s'assurer que tous les champs sont bien ajoutés
        setTimeout(function() {
            try {
                // Méthode 1: Utiliser l'élément DOM natif
                const formElement = form[0];
                if (formElement) {
                    console.log('Soumission via formElement.submit()');
                    console.log('Action finale:', formElement.action);
                    console.log('Méthode finale:', formElement.method);
                    
                    // Vérifier une dernière fois que les champs sont présents
                    const finalCheck = {
                        date: form.find('input[name="date"]').val(),
                        start_time: form.find('input[name="start_time"]').val(),
                        end_time: form.find('input[name="end_time"]').val(),
                        staff_member: form.find('select[name="staff_member"]').val()
                    };
                    console.log('Vérification finale avant soumission:', finalCheck);
                    
                    if (finalCheck.date && finalCheck.start_time && finalCheck.end_time && finalCheck.staff_member && finalCheck.staff_member !== 'none') {
                        // Soumettre le formulaire
                        formElement.submit();
                        console.log('✓ Formulaire soumis avec succès');
                    } else {
                        console.error('❌ Champs manquants lors de la vérification finale:', finalCheck);
                        alert('Erreur: Certains champs sont manquants. Veuillez réessayer.');
                        $('.btn-submit-appointment').prop('disabled', false);
                    }
                } else {
                    console.error('❌ Élément formulaire non trouvé!');
                    alert('Erreur: Formulaire non trouvé. Veuillez recharger la page.');
                    $('.btn-submit-appointment').prop('disabled', false);
                }
            } catch (error) {
                console.error('❌ Erreur lors de la soumission du formulaire:', error);
                console.error('Stack trace:', error.stack);
                alert('Erreur lors de la soumission du formulaire. Veuillez réessayer.');
                $('.btn-submit-appointment').prop('disabled', false);
            }
        }, 50); // Petit délai de 50ms pour s'assurer que tout est prêt
    } else {
        console.error('❌ Condition non remplie: selectedSlot ou selectedDateIso manquant');
        console.error('  - selectedSlot:', selectedSlot);
        console.error('  - selectedDateIso:', selectedDateIso);
        const warningContainer = $('.warning-message');
        if (warningContainer.length === 0 || warningContainer.find('.submit-warning').length === 0) {
            if (warningContainer.length === 0) {
                // Créer le conteneur s'il n'existe pas
                $('body').append('<div class="warning-message"></div>');
                warningContainer = $('.warning-message');
            }
            warningContainer.append('<p class="submit-warning">' + selectTimeSlotWarningTxt + '</p>');
        }
        alert(selectTimeSlotWarningTxt);
    }
});

$('#staff_id').on('change', function () {
    staffId = $(this).val() || null;  // If staffId is an empty string, set it to null
    
    // Si le calendrier n'est pas encore initialisé, l'initialiser
    if (!window.calendar && !calendar) {
        console.log('Calendrier non initialisé, initialisation...');
        // Réinitialiser le compteur pour permettre une nouvelle tentative
        initializationAttempts = 0;
        initializeCalendar();
        // Attendre un peu pour que le calendrier s'initialise
        setTimeout(function() {
            handleStaffChange();
        }, 500);
    } else {
        handleStaffChange();
    }
    
    function handleStaffChange() {
        let currentDate = null;
        if (selectedDate == null) {
            if (typeof moment !== 'undefined' && typeof timezone !== 'undefined') {
                currentDate = moment.tz(timezone).format('YYYY-MM-DD');
            } else {
                currentDate = new Date().toISOString().split('T')[0];
            }
        } else {
            currentDate = selectedDate;
        }
        
        fetchNonWorkingDays(staffId, function (newNonWorkingDays) {
            if (!window.calendar && !calendar) {
                console.warn('Calendrier toujours non initialisé après sélection du membre du personnel');
                return;
            }
            
            nonWorkingDays = newNonWorkingDays;  // Update the nonWorkingDays array
            const cal = window.calendar || calendar;
            if (cal && typeof cal.render === 'function') {
                // S'assurer que le calendrier est visible
                const calendarEl = document.getElementById('calendar');
                if (calendarEl) {
                    calendarEl.style.display = 'block';
                    calendarEl.style.visibility = 'visible';
                    calendarEl.style.opacity = '1';
                    calendarEl.style.width = '100%';
                    calendarEl.style.minHeight = '350px';
                }
                
                try {
                    cal.render();
                    window.calendar = cal;
                    calendar = cal;
                } catch(renderError) {
                    console.warn('Erreur lors du rendu du calendrier:', renderError);
                }
                
                // Forcer l'affichage après le rendu
                setTimeout(function() {
                    if (calendarEl) {
                        const viewHarness = calendarEl.querySelector('.fc-view-harness');
                        if (viewHarness) {
                            viewHarness.style.display = 'block';
                            viewHarness.style.visibility = 'visible';
                            viewHarness.style.opacity = '1';
                        } else {
                            console.warn('View harness non trouvé après rendu');
                        }
                    }
                }, 100);
            } else {
                console.warn('Calendrier non disponible ou méthode render() absente');
            }

            // Fetch available slots for the current date
            getAvailableSlots(currentDate, staffId);
        });
    }
});


function fetchNonWorkingDays(staffId, callback) {
    if (!staffId || staffId === 'none') {
        nonWorkingDays = [];  // Reset nonWorkingDays
        if (window.calendar || calendar) {
            const cal = window.calendar || calendar;
            if (cal && typeof cal.render === 'function') {
                try {
                    cal.render();
                    window.calendar = cal;
                    calendar = cal;
                } catch(e) {
                    console.warn('Erreur lors du rendu:', e);
                }
            }
        }
        callback([]);
        return;  // Exit the function early
    }
    let ajaxData = {
        'staff_member': staffId,
    };

    $.ajax({
        url: getNonWorkingDaysURL,
        data: ajaxData,
        dataType: 'json',
        success: function (data) {
            if (data.error) {
                console.error('Error fetching non-working days:', data.message);
                callback([]);
            } else {
                nonWorkingDays = data.non_working_days;
                if (window.calendar || calendar) {
                    const cal = window.calendar || calendar;
                    if (cal && typeof cal.render === 'function') {
                        try {
                            cal.render();
                            window.calendar = cal;
                            calendar = cal;
                        } catch(e) {
                            console.warn('Erreur lors du rendu:', e);
                        }
                    }
                }
                callback(data.non_working_days);
            }
        },
        error: function(xhr, status, error) {
            console.error('Erreur AJAX lors de la récupération des jours non travaillés:', error);
            callback([]);
        }
    });
}

function getDateWithoutTime(dt) {
    dt.setHours(0, 0, 0, 0);
    return dt;
}

function convertTo24Hour(time12h) {
    const [time, modifier] = time12h.split(' ');
    let [hours, minutes] = time.split(':');

    if (hours === '12') {
        hours = '00';
    }

    if (modifier.toUpperCase() === 'PM') {
        hours = parseInt(hours, 10) + 12;
    }

    return `${hours}:${minutes}`;
}

function formatTime(date) {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    return (hours < 10 ? '0' + hours : hours) + ':' + (minutes < 10 ? '0' + minutes : minutes);
}

function getAvailableSlots(selectedDate, staffId = null) {
    console.log('=== getAvailableSlots APPELÉ ===');
    console.log('Date sélectionnée:', selectedDate);
    console.log('Staff ID:', staffId);
    
    // Update the slot list with the available slots for the selected date
    const slotList = $('#slot-list');
    const slotContainer = $('.slot-container');
    const errorMessageContainer = $('.error-message');

    // Clear previous error messages and slots
    slotList.empty();
    errorMessageContainer.find('.djangoAppt_no-availability-text').remove();

    // Remove the "Next available date" message
    nextAvailableDateSelector = $('.djangoAppt_next-available-date'); // Update the selector
    nextAvailableDateSelector.remove();

    // Correctly check if staffId is 'none', null, or undefined and exit the function if true
    // Check if 'staffId' is 'none', null, or undefined and display an error message
    if (staffId === 'none' || staffId === null || staffId === undefined) {
        console.error('❌ No staff ID provided, displaying error message.');
        const errorMessage = $('<p class="djangoAppt_no-availability-text">' + noStaffMemberSelectedTxt + '</p>');
        errorMessageContainer.empty().append(errorMessage).show();
        // Désactiver le bouton si pas de staff sélectionné
        updateSubmitState();
        return; // Exit the function early
    }

    let ajaxData = {
        'selected_date': selectedDate,
        'staff_member': staffId,
    };
    fetchNonWorkingDays(staffId, function (nonWorkingDays) {
        // Check if nonWorkingDays is an array
        if (Array.isArray(nonWorkingDays)) {
            // Update the FullCalendar configuration
            // calendar.setOption('hiddenDays', nonWorkingDays);
        } else {
            // Handle the case where there's an error or no data
            // For now, we'll just log it, but you can handle it more gracefully if needed
            console.error('Failed to get non-working days:', nonWorkingDays);
        }
    });

    // Send an AJAX request to get the available slots for the selected date
    if (isRequestInProgress) {
        return; // Exit the function if a request is already in progress
    }
    isRequestInProgress = true;
    $.ajax({
        url: availableSlotsAjaxURL,
        data: ajaxData,
        dataType: 'json',
        success: function (data) {
            console.log('=== RÉPONSE AJAX POUR LES CRÉNEAUX ===');
            console.log('Success:', data.success);
            console.log('Message:', data.message);
            console.log('Date choisie:', data.date_chosen);
            console.log('Staff member:', data.staff_member);
            console.log('Nombre de créneaux:', data.available_slots ? data.available_slots.length : 0);
            console.log('Créneaux disponibles:', data.available_slots);
            console.log('Données complètes:', data);
            
            // Vérifier si data.available_slots existe
            if (!data.available_slots) {
                console.error('ERREUR: data.available_slots est undefined ou null');
                errorMessageContainer
                    .empty()
                    .append('<p class="djangoAppt_no-availability-text">Erreur: Aucune donnée de créneaux reçue</p>')
                    .show();
                isRequestInProgress = false;
                updateSubmitState();
                return;
            }
            
            if (data.available_slots.length === 0) {
                console.log('⚠️ Aucun créneau disponible pour cette date');
                const selectedDateObj = moment.tz(selectedDate, timezone);
                const selectedD = selectedDateObj.toDate();
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                if (selectedD < today) {
                    // Show an error message
                    errorMessageContainer
                        .empty()
                        .append('<p class="djangoAppt_no-availability-text">' + dateInPastErrorTxt + '</p>')
                        .show();
                    if (slotContainer.find('.djangoAppt_btn-request-next-slot').length === 0) {
                        slotContainer.append(`<button class="btn btn-danger djangoAppt_btn-request-next-slot" data-service-id="${serviceId}">` + requestNonAvailableSlotBtnTxt + `</button>`);
                    }
                    // Disable the 'submit' button
                    $('.btn-submit-appointment').attr('disabled', 'disabled');
                } else {
                    // Afficher un message explicite si aucun créneau n'est disponible
                    let messageText = data.message || 'Aucun créneau disponible pour cette date';
                    
                    // Si le message indique que les créneaux ont été récupérés avec succès mais la liste est vide,
                    // cela signifie probablement qu'aucun horaire de travail n'est configuré
                    if (data.success && data.message && data.message.includes('récupérés avec succès')) {
                        messageText = 'Aucun créneau disponible. Veuillez vérifier que des horaires de travail sont configurés pour ce membre du personnel.';
                        console.warn('⚠️ Aucun créneau disponible - Vérifiez les horaires de travail (WorkingHours) pour:', data.staff_member);
                    }
                    
                    errorMessageContainer.find('.djangoAppt_no-availability-text').remove().end().show();
                    if (errorMessageContainer.find('.djangoAppt_no-availability-text').length === 0) {
                        errorMessageContainer.append(`<p class="djangoAppt_no-availability-text">${messageText}</p>`);
                    }
                    // Check if the returned message is 'No availability'
                    if (data.message && (data.message.toLowerCase() === 'no availability' || data.message.toLowerCase().includes('aucun créneau'))) {
                        if (slotContainer.find('.djangoAppt_btn-request-next-slot').length === 0) {
                            slotContainer.append(`<button class="btn btn-danger djangoAppt_btn-request-next-slot" data-service-id="${serviceId}">` + requestNonAvailableSlotBtnTxt + `</button>`);
                        }
                    } else {
                        $('.djangoAppt_btn-request-next-slot').remove();
                    }
                }
            } else {
                console.log('✓ Créneaux disponibles trouvés:', data.available_slots.length);
                // remove the button to request for next available slot
                $('.djangoAppt_no-availability-text').remove();
                $('.djangoAppt_btn-request-next-slot').remove();
                
                // Vider la liste avant d'ajouter les nouveaux créneaux
                slotList.empty();
                
                const uniqueSlots = [...new Set(data.available_slots)]; // remove duplicates
                console.log('Créneaux uniques après déduplication:', uniqueSlots);
                
                if (uniqueSlots.length === 0) {
                    console.warn('Aucun créneau unique après déduplication');
                    errorMessageContainer
                        .empty()
                        .append('<p class="djangoAppt_no-availability-text">Aucun créneau disponible pour cette date</p>')
                        .show();
                } else {
                    for (let i = 0; i < uniqueSlots.length; i++) {
                        const slotItem = $('<li class="djangoAppt_appointment-slot" role="button" tabindex="0" aria-label="Sélectionner le créneau ' + uniqueSlots[i] + '">' + uniqueSlots[i] + '</li>');
                        slotList.append(slotItem);
                        console.log('Créneau ajouté:', uniqueSlots[i]);
                    }
                    console.log('✓ Total de créneaux ajoutés à la liste:', slotList.find('li').length);
                    
                    // Vérifier que le conteneur est visible
                    const slotContainerEl = slotList.closest('.slot-container');
                    if (slotContainerEl.length > 0) {
                        console.log('Conteneur des créneaux trouvé:', slotContainerEl);
                        slotContainerEl.show();
                        console.log('Visibilité du conteneur:', slotContainerEl.is(':visible'));
                    } else {
                        console.warn('Conteneur .slot-container non trouvé');
                    }
                    
                    // Vérifier que la liste est visible
                    console.log('Visibilité de la liste:', slotList.is(':visible'));
                    console.log('Nombre d\'éléments dans le DOM:', slotList.find('li').length);
                }

                // Attach click event to the slots
                $('.djangoAppt_appointment-slot').on('click', function () {
                    selectSlot($(this), data.date_chosen);
                });
                
                // Attach keyboard event for accessibility
                $('.djangoAppt_appointment-slot').on('keydown', function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        selectSlot($(this), data.date_chosen);
                    }
                });
                
                function selectSlot($slot, dateChosen) {
                    // Remove the 'selected' class from all other appointment slots
                    $('.djangoAppt_appointment-slot').removeClass('selected');

                    // Add the 'selected' class to the clicked appointment slot
                    $slot.addClass('selected');

                    // Définir selectedDateIso uniquement quand un créneau est sélectionné
                    // Utiliser la date ISO de la réponse AJAX
                    if (data.date_iso) {
                        selectedDateIso = data.date_iso;
                    } else {
                        // Fallback: utiliser selectedDate si disponible
                        selectedDateIso = selectedDate || null;
                    }

                    // Mettre à jour l'état du bouton
                    updateSubmitState();

                    // Continue with the existing logic
                    const selectedSlot = $slot.text();
                    $('#service-datetime-chosen').text(dateChosen + ' ' + selectedSlot);
                }
                // Quand on a des créneaux, masquer le panneau d'erreur
                errorMessageContainer.hide();
            }
            // Update the date chosen
            // Ne PAS définir selectedDateIso ici - il sera défini uniquement quand un créneau est sélectionné
            // Garder selectedDateIso à null jusqu'à ce qu'un créneau soit sélectionné
            // selectedDateIso sera défini dans selectSlot() quand un créneau est cliqué
            $('.djangoAppt_date_chosen').text(data.date_chosen);
            // Ne mettre à jour #service-datetime-chosen que si aucun créneau n'est sélectionné
            if ($('.djangoAppt_appointment-slot.selected').length === 0) {
                $('#service-datetime-chosen').text(data.date_chosen);
            }
            // Mettre à jour l'état du bouton après chargement des créneaux
            // Le bouton doit rester désactivé car aucun créneau n'est encore sélectionné
            updateSubmitState();
            isRequestInProgress = false;
        },
        error: function(xhr, status, error) {
            console.error('=== ERREUR AJAX LORS DE LA RÉCUPÉRATION DES CRÉNEAUX ===');
            console.error('Status:', status);
            console.error('Error:', error);
            console.error('Response:', xhr.responseText);
            console.error('Status Code:', xhr.status);
            
            isRequestInProgress = false; // Ensure the flag is reset even if the request fails
            
            // Afficher un message d'erreur à l'utilisateur
            let errorMessage = 'Erreur lors de la récupération des créneaux. ';
            if (xhr.status === 0) {
                errorMessage += 'Vérifiez votre connexion internet.';
            } else if (xhr.status === 400) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || errorMessage;
                } catch (e) {
                    errorMessage += 'Requête invalide.';
                }
            } else if (xhr.status === 500) {
                errorMessage += 'Erreur serveur. Veuillez réessayer plus tard.';
            } else {
                errorMessage += `Erreur ${xhr.status}: ${error}`;
            }
            
            errorMessageContainer
                .empty()
                .append(`<p class="djangoAppt_no-availability-text">${errorMessage}</p>`)
                .show();
            
            updateSubmitState();
        }
    });
}

function requestNextAvailableSlot(serviceId) {
    const requestNextAvailableSlotURL = requestNextAvailableSlotURLTemplate.replace('0', serviceId);
    if (staffId === null) {
        return;
    }
    let ajaxData = {
        'staff_member': staffId,
    };
    $.ajax({
        url: requestNextAvailableSlotURL,
        data: ajaxData,
        dataType: 'json',
        success: function (data) {
            // If there's an error, just log it and return
            let nextAvailableDateResponse = null;
            let formattedDate = null;
            if (data.error) {
                nextAvailableDateResponse = data.message;
            } else {
                // Set the date in the calendar to the next available date
                nextAvailableDateResponse = data.next_available_date;
                const selectedDateObj = moment.tz(nextAvailableDateResponse, timezone);
                const nextAvailableDate = selectedDateObj.toDate()
                formattedDate = new Intl.DateTimeFormat(locale, {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }).format(nextAvailableDate);

                // Naviguer vers cette date et charger les créneaux
                try {
                    if (window.calendar && typeof window.calendar.gotoDate === 'function') {
                        window.calendar.gotoDate(nextAvailableDate);
                    }
                } catch (_) {}
                // Mettre à jour l'UI et relancer le chargement des créneaux
                const iso = selectedDateObj.format('YYYY-MM-DD');
                selectedDate = iso;
                selectedDateIso = iso;
                $('.djangoAppt_date_chosen').text(formattedDate);
                getAvailableSlots(iso, staffId);
            }

            // Check if the .next-available-date element already exists
            nextAvailableDateSelector = $('.djangoAppt_next-available-date'); // Update the selector
            let nextAvailableDateText = null;
            if (data.error) {
                nextAvailableDateText = nextAvailableDateResponse;
            } else {
                nextAvailableDateText = `${nextAvailableDateTxt}: ${formattedDate}`;
            }
            if (nextAvailableDateSelector.length > 0) {
                // Update the content of the existing .next-available-date element
                nextAvailableDateSelector.text(nextAvailableDateText);
            } else {
                // If the .next-available-date element doesn't exist, create and append it
                const nextDateText = `<p class="djangoAppt_next-available-date">${nextAvailableDateText}</p>`;
                $('.djangoAppt_btn-request-next-slot').after(nextDateText);
            }
        }
    });
}
