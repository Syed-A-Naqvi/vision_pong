/**
 * @typedef {object} UpdateThemeMessageData
 * @property {string} type - The type of message, should be "update-theme"
 * @property {{"light"|"dark"}} theme - The theme to update to, either "light" or "dark"
 */

(function() {

    'use strict';
    
    // ============================================================================
    // CONSTANTS
    // ============================================================================
    
    const MESSAGE_TYPE_UPDATE_THEME = "update-theme";
    const THEME_DARK = "dark";
    const THEME_LIGHT = "light";
    const IFRAME_STYLESHEET_HREF_PARTIAL = "_static/portfolio-sync.css";
    const DATA_THEME_ATTRIBUTE = "data-theme";
    const DATA_MODE_ATTRIBUTE = "data-mode";
    const LOCAL_STORAGE_THEME_KEY = "theme";
    const LOCAL_STORAGE_MODE_KEY = "mode";
    const TRUSTED_ORIGINS = [
        // for loacl development
        "http://127.0.0.1:5501",
        "http://127.0.0.1:5500",
        // production
        "https://syed-a-naqvi.github.io"
    ];
    
    // ============================================================================
    // THEME MANAGEMENT
    // ============================================================================
    
    /**
     * Applies theme to HTML element and persists to local storage
     * @param {string} theme - "light" or "dark"
     */
    function applyTheme(theme) {
        const htmlElement = document.documentElement;
        htmlElement.setAttribute(DATA_THEME_ATTRIBUTE, theme);
        htmlElement.setAttribute(DATA_MODE_ATTRIBUTE, theme);
        localStorage.setItem(LOCAL_STORAGE_THEME_KEY, theme);
        localStorage.setItem(LOCAL_STORAGE_MODE_KEY, theme);
    }

    /**
     * Handles theme update messages from parent window
     * @param {MessageEvent<UpdateThemeMessageData>} event
     */
    function handleThemeMessage(event) {
        if (event.data.type !== MESSAGE_TYPE_UPDATE_THEME) return;
        if (!TRUSTED_ORIGINS.includes(event.origin)) {
            console.warn("Untrusted origin:", event.origin);
            return;
        }
        
        if (event.data.theme === THEME_DARK || event.data.theme === THEME_LIGHT) {
            applyTheme(event.data.theme);
        } else {
            console.warn("Invalid theme received:", event.data.theme);
        }
    }

    
    // ============================================================================
    // UI CLEANUP FOR IFRAME CONTEXT
    // ============================================================================

    /**
     * Removes iframe-specific stylesheet when in standalone context
     */
    function removeIframeSpecificStylesheet() {
        const linkElements = document.head.querySelectorAll("link[rel='stylesheet']");
        
        for (const link of linkElements) {
            if (link.href.includes(IFRAME_STYLESHEET_HREF_PARTIAL)) {
                link.remove();
                return;
            }
        }
    }

    /**
     * Removes UI elements irrelevant in iframe context
     */
    function removeButtonsInIframeContext() {
        [".theme-switch-button", ".btn-fullscreen-button"].forEach(selector => {
            document.querySelector(selector)?.remove();
        });
    }

    /**
     * Prevents horizontal scrolling in iframe context
     */
    function removeHorizontalScroll() {
        document.body.style.overflowX = "hidden";
    }
    
    // ============================================================================
    // CUSTOM SCROLLSPY IMPLEMENTATION
    // ============================================================================

    /**
     * Custom ScrollSpy for iframe context
     * 180px top offset, -80% bottom margin
     */
    let scrollSpyInitialized = false;
    
    function initializeCustomScrollSpy() {

        // Prevent duplicate initialization
        if (scrollSpyInitialized) return;
        scrollSpyInitialized = true;
        
        // Remove Bootstrap ScrollSpy
        const bodyElement = document.body;
        bodyElement.removeAttribute('data-bs-spy');
        bodyElement.removeAttribute('data-bs-target');
        bodyElement.removeAttribute('data-offset');
        bodyElement.removeAttribute('data-bs-root-margin');
        
        if (window.bootstrap?.ScrollSpy) {
            const existingInstance = window.bootstrap.ScrollSpy.getInstance(bodyElement);
            existingInstance?.dispose();
        }
        
        // Find TOC navigation
        const tocNav = document.querySelector('.bd-toc-nav');
        if (!tocNav) return;
        
        // Initialize data structures
        const sectionLinkMap = new Map();
        const childToParentMap = new Map();
        const tocLinks = Array.from(tocNav.querySelectorAll('a.nav-link[href^="#"]'));
        const activeLinks = [];

        // observer object declaration and state tracking
        let observer = null;
        let observerActive = false;
        
        // activate link and all parents
        function setActiveLink(link) {
            if (!link) return;
            
            // Clear currently active links
            while (activeLinks.length > 0) {
                const l = activeLinks.pop();
                l.classList.remove('active');
                l.closest('li')?.classList.remove('active');
            }
            
            // Activate link and parents hierarchically
            let currentLink = link;
            while (currentLink) {
                currentLink.classList.add('active');
                currentLink.closest('li')?.classList.add('active');
                activeLinks.push(currentLink);
                currentLink = childToParentMap.get(currentLink);
            }
        }

        // function for enabling and disabling intersection observer
        function toggleObserver(enable) {
            if (enable) {
                try {
                    // observing each section
                    sectionLinkMap.forEach((link, section) => {
                        observer.observe(section);
                    });
                    observerActive = true;
                }
                catch (e) {
                    console.warn("Failed to observe section:", e);
                }
            } else {
                try {
                    observer.disconnect();
                    observerActive = false;
                }
                catch (e) {
                    console.warn("Failed to disconnect observer:", e);
                }
            }
        }

        // Calculate responsive rootMargin based on viewport size
        function getResponsiveObserver() {
            const viewportHeight = window.innerHeight;
            const viewportWidth = window.innerWidth;
                        
            // Top offset: smaller on mobile
            let observerTopMargin = 70;
            
            // Bottom margin: more conservative on mobile
            // Use pixel values instead of percentages for better reliability
            // Keep a single pixel width to avoid edge cases
            let observerBottomMargin = viewportHeight - observerTopMargin - 1;

            const margin = `-${observerTopMargin}px 0px -${observerBottomMargin}px 0px`;
            console.log(`[ScrollSpy] Viewport: ${viewportWidth}x${viewportHeight}, RootMargin: ${margin}`);

            return new IntersectionObserver((entries) => {
            
                entries.forEach(entry => {
                    if (entry.isIntersecting) {

                        const targetSection = entry.target;
                        setActiveLink(sectionLinkMap.get(targetSection));

                    }
                });
            }, {
                root: null,
                rootMargin: margin,
                threshold: 0
            });
        }
        
        // Build mappings and attach click handlers
        tocLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href || href === '#') return;
            
            // Map section to link
            const targetId = href.slice(1);
            const targetSection = document.getElementById(targetId);
            sectionLinkMap.set(targetSection, link);
            
            // Build parent-child hierarchy
            const parentLi = link.closest('li');
            const parentUl = parentLi?.parentElement;
            if (parentUl?.classList.contains('nav')) {
                const grandparentLi = parentUl.closest('li');
                const parentLink = grandparentLi?.querySelector('a.nav-link');
                if (parentLink) childToParentMap.set(link, parentLink);
            }
            
            link.addEventListener('mousedown', (e) => {
                // Prevent mousedown from enabling observer
                e.stopPropagation();
            });

            // Smooth scroll on click
            link.addEventListener('click', (e) => {

                e.preventDefault();
                
                if (targetSection) {

                    // disable observer during manual scroll
                    if (observerActive) {
                        toggleObserver(false);
                    }
                    targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    setActiveLink(link);

                }
            });
        });

        // Observe all sections
        ['wheel', 'keydown', 'mousedown', 'touchstart'].forEach(eventType => {
            // This may be a user-initiated scroll
            window.addEventListener(eventType, (e) => {

                // no need to rebuild intersection observer if it already exists
                if (!observerActive){
                    toggleObserver(true);
                }

            }, { passive: true });
        });
        
        // Handle viewport resize (important for responsive design mode)
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                console.log('[ScrollSpy] Viewport resized, reinitializing observer...');
                toggleObserver(false);

                observer = getResponsiveObserver();

                toggleObserver(true);
            }, 1000); // Debounce resize events
        });
        
        // Initializing page startup state
        // removing any active links
        sectionLinkMap.forEach((link, section) => {
            link.classList.remove('active');
            link.closest('li')?.classList.remove('active');
        });
        // setting first section as active
        const firstSection = sectionLinkMap.keys().next().value;
        if (firstSection) {
            const link = sectionLinkMap.get(firstSection);
            if (link) setActiveLink(link);
        }

        // creating observer object
        observer = getResponsiveObserver();
        // Start observing
        toggleObserver(true);

        // creating an overlay to visualize the rootMargin area (for debugging)
        // const overlay = document.createElement('div');
        // overlay.style.position = 'fixed';
        // overlay.style.top = `${observerTopMargin}px`;
        // overlay.style.left = '0';
        // overlay.style.width = '100%';
        // overlay.style.height = `calc(100% - ${observerTopMargin}px - ${observerBottomMargin}px)`;
        // overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
        // overlay.style.pointerEvents = 'none';
        // overlay.style.zIndex = '9999';
        // document.body.appendChild(overlay);

    }
    
    // ============================================================================
    // INITIALIZATION
    // ============================================================================

    /**
     * Initialize all features based on context (iframe vs standalone)
     */
    function initialize() {
       
        const isIframe = window.self !== window.top;
        
        if (isIframe) {

            // Iframe context UI cleanup
            removeButtonsInIframeContext();
            removeHorizontalScroll();

            // Listen for theme update messages
            window.addEventListener("message", handleThemeMessage);
            
            // Initialize ScrollSpy on first user interaction
            ['mousemove', 'scroll', 'touchstart', 'click'].forEach(eventType => {
                window.addEventListener(eventType, initializeCustomScrollSpy, { 
                    once: true, 
                    passive: true 
                });
            });

        } else {
       
            // Standalone context: remove iframe-specific styles
            removeIframeSpecificStylesheet();
       
        }
    }
    
    // Start when DOM is ready
    document.addEventListener("DOMContentLoaded", initialize);

})();