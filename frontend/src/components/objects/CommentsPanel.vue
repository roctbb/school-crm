<template>
    <section class="comments-panel card">
        <div class="card-header py-3">
            <h5 class="mb-0">
                Комментарии <i v-if="commentsHidden" class="ms-1 bi bi-eye-slash"></i>
            </h5>
        </div>
        <div class="card-body">
        <!-- Список комментариев -->
        <div v-for="comment in sortedComments" :key="comment.id" class="mb-3">
            <!-- Шапка: автор, время и иконка удаления -->
            <div class="d-flex align-items-center">
                <div class="fw-bold">
                    {{ comment.author ? comment.author.name : 'Неизвестный пользователь' }}
                </div>
                <div class="text-muted ms-2" style="font-size: 0.85rem;">
                    {{ formatDate(comment.created_at) }}
                </div>
                <!-- Иконка удаления справа -->
                <button
                    v-if="canDeleteComment(comment)"
                    class="btn btn-sm btn-link text-danger ms-auto p-1"
                    type="button"
                    title="Удалить комментарий"
                    :aria-label="`Удалить комментарий пользователя ${comment.author?.name || ''}`"
                    @click="removeComment(comment)"
                >
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            <!-- Текст комментария -->
            <div>{{ comment.text }}</div>
            <hr class="my-3"/>
        </div>

        <!-- Форма добавления нового комментария -->
        <div :class="sortedComments.length ? 'mt-3' : ''" v-if="canCommentObject(object)">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <form @submit.prevent="postComment">
                <div class="mb-3">
                    <textarea
                        class="form-control"
                        rows="3"
                        v-model="newComment"
                        placeholder="Напишите свой комментарий..."
                        aria-label="Новый комментарий"
                    />
                </div>
                <button class="btn btn-primary btn-sm" type="submit" :disabled="!newComment.trim()">Отправить</button>
            </form>
        </div>
        </div>
    </section>
</template>

<script>
import {postComment, deleteComment} from "@/api/objects_api.js";
import {canCommentObject, canDeleteComment} from "@/utils/access.js";
import useMainStore from "@/stores/mainStore.js";

export default {
    name: "CommentsPanel",
    props: {
        object: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            newComment: "",
            store: useMainStore(),
            error: "",
        };
    },
    computed: {
        sortedComments() {
            // Сортируем комментарии по времени
            return [...this.object.comments].sort((a, b) => {
                return new Date(a.created_at) - new Date(b.created_at);
            });
        },
        commentsHidden() {
            return this.store.getObjectTypeByCode(this.object.type).params.comments_hidden
        }
    },
    methods: {
        canDeleteComment,
        canCommentObject,
        async postComment() {
            const text = this.newComment.trim();
            if (!text) return;

            try {
                this.error = "";
                const createdComment = await postComment(this.object.id, text);
                this.object.comments.push(createdComment);
                this.newComment = "";
            } catch (error) {
                this.error = error.message || "Не удалось добавить комментарий.";
                console.error("Ошибка при добавлении комментария:", error);
            }
        },
        async removeComment(comment) {
            if (!confirm("Вы действительно хотите удалить этот комментарий?")) {
                return;
            }
            try {
                this.error = "";
                await deleteComment(this.object.id, comment.id);
                this.object.comments = this.object.comments.filter(
                    (item) => item.id !== comment.id
                );
            } catch (error) {
                this.error = error.message || "Не удалось удалить комментарий.";
                console.error("Ошибка при удалении комментария:", error);
            }
        },
        formatDate(isoString) {
            return new Date(isoString).toLocaleString("ru-RU");
        }
    }
};
</script>

<style scoped>
.comments-panel {
    position: sticky;
    top: 5rem;
    overflow: hidden;
    background: var(--silaeder-surface);
}

.comments-panel .form-control {
    background: #fff;
}

@media (max-width: 991.98px) {
    .comments-panel {
        position: static;
    }
}
</style>
