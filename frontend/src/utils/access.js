import useMainStore from "@/stores/mainStore.js";

function hasAdminAccess() {
    const user = useMainStore().profile;
    return user?.role === 'admin';
}

function hasTeacherAccess() {
    const user = useMainStore().profile;
    return user?.role === 'teacher' || hasAdminAccess(user);
}

function canCreateByType(category) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (category?.params?.can_create?.includes(user.role)) {
        return true;
    }
    return false
}

function canFillInCategory(objectType) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (objectType?.params?.can_fill?.includes(user.role)) {
        return true;
    }
    return false
}

function canModifyObject(object) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (object?.owners?.some(owner => owner.id === user.id)) {
        return true;
    }
    return false
}

function canDeleteObject(object) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (object?.owners?.some(owner => owner.id === user.id) && !object.is_approved && object.params?.can_delete?.includes(user.role)) {
        return true;
    }
    return false
}

function canCommentObject(object) {
    const user = useMainStore().profile;
    const type = useMainStore().getObjectTypeByCode(object.type)

    if (hasTeacherAccess(user)) {
        return true;
    }
    if (type?.params?.can_fill?.includes(user.role)) {
        return true;
    }
    return false
}

function canDeleteComment(comment) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (user?.id === comment.creator.id) {
        return true;
    }
    return false
}

function canModifySubmission(submission) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (user?.id === submission.creator.id && !submission.is_approved) {
        return true;
    }
    return false
}

function canGetObjectType(objectType) {
    const user = useMainStore().profile;
    if (hasTeacherAccess(user)) {
        return true;
    }
    if (!objectType?.params?.is_hidden) {
        return true;
    }
    return false; // По умолчанию доступ запрещён
}

// Экспорт функций, если нужно использовать их в других модулях
export {
    hasAdminAccess,
    hasTeacherAccess,
    canCreateByType,
    canFillInCategory,
    canModifyObject,
    canDeleteObject,
    canCommentObject,
    canDeleteComment,
    canModifySubmission,
    canGetObjectType,
};