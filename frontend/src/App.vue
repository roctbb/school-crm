<template>
    <router-view/>
    <GlobalLoadingOverlay :visible="globalLoadingState.visible" />
</template>

<script>
import GlobalLoadingOverlay from '@/components/common/GlobalLoadingOverlay.vue';
import {globalLoadingState} from '@/services/globalLoading.js';

export default {
    name: "App",
    components: {GlobalLoadingOverlay},
    data() {
        return {globalLoadingState};
    },
};
</script>
