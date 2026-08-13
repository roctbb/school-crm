import {reactive} from 'vue';

const SHOW_DELAY = 250;
const MIN_VISIBLE_TIME = 350;

export const globalLoadingState = reactive({
    visible: false,
});

let pendingRequests = 0;
let navigationPending = false;
let showTimer = null;
let hideTimer = null;
let visibleSince = 0;

function isBusy() {
    return navigationPending || pendingRequests > 0;
}

function clearTimer(timer) {
    if (timer !== null) window.clearTimeout(timer);
}

function updateVisibility() {
    clearTimer(hideTimer);
    hideTimer = null;

    if (isBusy()) {
        if (globalLoadingState.visible || showTimer !== null) return;

        showTimer = window.setTimeout(() => {
            showTimer = null;
            if (!isBusy()) return;
            visibleSince = Date.now();
            globalLoadingState.visible = true;
        }, SHOW_DELAY);
        return;
    }

    clearTimer(showTimer);
    showTimer = null;

    if (!globalLoadingState.visible) return;

    const remainingTime = Math.max(0, MIN_VISIBLE_TIME - (Date.now() - visibleSince));
    hideTimer = window.setTimeout(() => {
        hideTimer = null;
        if (!isBusy()) globalLoadingState.visible = false;
    }, remainingTime);
}

export function startRequestLoading() {
    pendingRequests += 1;
    updateVisibility();
}

export function finishRequestLoading() {
    pendingRequests = Math.max(0, pendingRequests - 1);
    updateVisibility();
}

export function startNavigationLoading() {
    navigationPending = true;
    updateVisibility();
}

export function finishNavigationLoading() {
    navigationPending = false;
    updateVisibility();
}
