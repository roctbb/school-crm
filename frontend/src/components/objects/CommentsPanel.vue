<template>
    <div class="comments-panel mb-3">
        <h5>Комментарии</h5>
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
                <div
                    class="text-danger ms-auto"
                    style="cursor: pointer; font-size: 0.85rem;"
                    title="Удалить комментарий"
                    @click="removeComment(comment)"
                >
                    <i class="bi bi-trash"></i>
                </div>
            </div>
            <!-- Текст комментария -->
            <div>{{ comment.text }}</div>
            <hr/>
        </div>

        <!-- Форма добавления нового комментария -->
        <div class="mt-3" v-if="hasTeacherAccess()">
            <form @submit.prevent="postComment">
                <div class="mb-3">
                    <textarea
                        class="form-control"
                        rows="3"
                        v-model="newComment"
                        placeholder="Напишите свой комментарий..."
                    />
                </div>
                <button class="btn btn-primary btn-sm" type="submit">Отправить</button>
            </form>
        </div>
    </div>
</template>

<script>
import { postComment, deleteComment } from "@/api/objects_api.js";
import {hasTeacherAccess} from "@/utils/helpers.js";

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
        };
    },
    computed: {
        sortedComments() {
            // Сортируем комментарии по времени
            return [...this.object.comments].sort((a, b) => {
                return new Date(a.created_at) - new Date(b.created_at);
            });
        }
    },
    methods: {
        hasTeacherAccess,
        async postComment() {
            const text = this.newComment.trim();
            if (!text) return;

            try {
                const createdComment = await postComment(this.object.id, text);
                this.object.comments.push(createdComment);
                this.newComment = "";
            } catch (error) {
                console.error("Ошибка при добавлении комментария:", error);
            }
        },
        async removeComment(comment) {
            if (!confirm("Вы действительно хотите удалить этот комментарий?")) {
                return;
            }
            try {
                await deleteComment(this.object.id, comment.id);
                this.object.comments = this.object.comments.filter(
                    (item) => item.id !== comment.id
                );
            } catch (error) {
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
    border-left: 1px solid #ccc;
    padding-left: 1rem;
}
</style>