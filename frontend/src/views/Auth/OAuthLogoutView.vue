<template>
    <div class="d-flex justify-content-center align-items-center min-vh-100 text-muted">
        Завершаем сеанс…
    </div>
</template>

<script>
import useMainStore from '@/stores/mainStore.js';
import {fetchLogoutRedirect} from '@/api/oidc_api.js';

export default {
    name: 'OAuthLogoutView',
    async created() {
        try {
            const result = await fetchLogoutRedirect({
                client_id: this.$route.query.client_id,
                post_logout_redirect_uri: this.$route.query.post_logout_redirect_uri,
                id_token_hint: this.$route.query.id_token_hint,
                state: this.$route.query.state,
            });
            useMainStore().logout();
            window.location.replace(result.redirect_uri);
        } catch (_error) {
            useMainStore().logout();
            this.$router.replace('/login');
        }
    },
};
</script>
