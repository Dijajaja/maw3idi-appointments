/**
 * Fonctionnalités d'accessibilité WCAG
 * - Ajustement de la taille de police
 * - Navigation au clavier améliorée
 * - Lecture vocale
 */

(function() {
    'use strict';

    // ============================================
    // 1. AJUSTEMENT DE LA TAILLE DE POLICE
    // ============================================
    const FONT_SIZES = ['small', 'normal', 'large', 'xlarge', 'xxlarge'];
    let currentFontSizeIndex = 1; // 'normal' par défaut

    function initFontSize() {
        // Restaurer la taille sauvegardée
        const savedSize = localStorage.getItem('fontSize');
        if (savedSize) {
            currentFontSizeIndex = FONT_SIZES.indexOf(savedSize);
            if (currentFontSizeIndex === -1) currentFontSizeIndex = 1;
            applyFontSize(FONT_SIZES[currentFontSizeIndex]);
        } else {
            applyFontSize('normal');
        }
    }

    function applyFontSize(size) {
        document.body.className = document.body.className.replace(/font-size-\w+/g, '');
        document.body.classList.add(`font-size-${size}`);
        localStorage.setItem('fontSize', size);
    }

    function increaseFontSize() {
        if (currentFontSizeIndex < FONT_SIZES.length - 1) {
            currentFontSizeIndex++;
            applyFontSize(FONT_SIZES[currentFontSizeIndex]);
        }
    }

    function decreaseFontSize() {
        if (currentFontSizeIndex > 0) {
            currentFontSizeIndex--;
            applyFontSize(FONT_SIZES[currentFontSizeIndex]);
        }
    }

    // ============================================
    // 2. NAVIGATION AU CLAVIER
    // ============================================
    function enhanceKeyboardNavigation() {
        // Ajouter tabindex="0" aux éléments interactifs qui n'en ont pas
        const interactiveElements = document.querySelectorAll(
            'button:not([tabindex]), a:not([tabindex]):not([href=""]), input:not([tabindex]):not([type="hidden"]), select:not([tabindex]), textarea:not([tabindex]), [role="button"]:not([tabindex]), [role="link"]:not([tabindex]), .fc-button:not([tabindex]), .djangoAppt_appointment-slot:not([tabindex])'
        );
        
        interactiveElements.forEach(el => {
            // Ignorer les éléments déjà désactivés
            if (el.disabled || el.hasAttribute('aria-hidden') || el.style.display === 'none') {
                return;
            }
            
            if (!el.hasAttribute('tabindex')) {
                el.setAttribute('tabindex', '0');
            }
        });

        // Gérer la navigation avec les flèches pour les listes et slots
        document.addEventListener('keydown', function(e) {
            const focused = document.activeElement;
            
            // Navigation dans les listes avec flèches
            if (focused && focused.tagName === 'LI' && focused.hasAttribute('tabindex')) {
                const listItems = Array.from(focused.parentElement.querySelectorAll('li[tabindex]'));
                const currentIndex = listItems.indexOf(focused);
                
                if (e.key === 'ArrowDown' && currentIndex < listItems.length - 1) {
                    e.preventDefault();
                    e.stopPropagation();
                    listItems[currentIndex + 1].focus();
                    return false;
                } else if (e.key === 'ArrowUp' && currentIndex > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                    listItems[currentIndex - 1].focus();
                    return false;
                } else if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    focused.click();
                    return false;
                }
            }
            
            // Navigation dans les slots de rendez-vous
            if (focused && focused.classList.contains('djangoAppt_appointment-slot')) {
                const slots = Array.from(document.querySelectorAll('.djangoAppt_appointment-slot[tabindex]'));
                const currentIndex = slots.indexOf(focused);
                
                if (e.key === 'ArrowRight' && currentIndex < slots.length - 1) {
                    e.preventDefault();
                    e.stopPropagation();
                    slots[currentIndex + 1].focus();
                    return false;
                } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                    slots[currentIndex - 1].focus();
                    return false;
                } else if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    focused.click();
                    return false;
                }
            }
        }, true); // Utiliser capture phase pour intercepter avant le scroll
    }

    // ============================================
    // 3. CRÉATION DU PANNEAU D'ACCESSIBILITÉ
    // ============================================
    function createAccessibilityPanel() {
        const panel = document.createElement('div');
        panel.className = 'accessibility-panel';
        panel.setAttribute('role', 'toolbar');
        panel.setAttribute('aria-label', 'Ajustement de la taille du texte');

        panel.innerHTML = `
            <button id="accessibility-font-decrease" 
                    aria-label="Réduire la taille du texte" 
                    title="Réduire la taille du texte">
                <i class="fas fa-minus"></i>
            </button>
            <button id="accessibility-font-increase" 
                    aria-label="Augmenter la taille du texte" 
                    title="Augmenter la taille du texte">
                <i class="fas fa-plus"></i>
            </button>
        `;

        document.body.appendChild(panel);

        // Événements
        document.getElementById('accessibility-font-increase').addEventListener('click', increaseFontSize);
        document.getElementById('accessibility-font-decrease').addEventListener('click', decreaseFontSize);

        // Navigation au clavier pour les boutons
        panel.querySelectorAll('button').forEach(btn => {
            btn.setAttribute('tabindex', '0');
        });
    }

    // ============================================
    // INITIALISATION
    // ============================================
    function init() {
        // Attendre que le DOM soit chargé
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                initFontSize();
                // createAccessibilityPanel(); // Désactivé
                enhanceKeyboardNavigation();
            });
        } else {
            initFontSize();
            // createAccessibilityPanel(); // Désactivé
            enhanceKeyboardNavigation();
        }

        // Réappliquer la navigation améliorée après les chargements dynamiques
        const observer = new MutationObserver(function() {
            enhanceKeyboardNavigation();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Démarrer
    init();

})();

