import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/repositories/progress_repository.dart';
import '../domain/models/lesson_resume.dart';
import 'app_controller.dart';

/// Holds the saved in-progress lessons (`lessonResume.v1`) and writes them
/// through on every change, so a lesson survives back-navigation, an app kill,
/// or a phone restart. Separate from [AppController] so the per-answer saves
/// do not rebuild every screen that watches the main app state.
class LessonResumeController extends AsyncNotifier<LessonResumeBook> {
  late ProgressRepository _repo;

  @override
  Future<LessonResumeBook> build() async {
    final store = await ref.watch(keyValueStoreProvider.future);
    _repo = ProgressRepository(store);
    return _repo.loadLessonResume();
  }

  /// Saves (or replaces) one lesson's in-progress state.
  Future<void> save(LessonResume resume) => _update((book) => book.put(resume));

  /// Forgets one lesson's in-progress state (finished, restarted, or stale).
  Future<void> clear(String examId, String lessonId) =>
      _update((book) => book.remove(examId, lessonId));

  /// Applies [change] to the in-memory book, then persists the whole (small)
  /// book. Calls are applied in order, so the last write always wins on disk.
  Future<void> _update(
    LessonResumeBook Function(LessonResumeBook) change,
  ) async {
    final loaded = await future;
    // Re-read: an earlier queued call may have changed the book meanwhile.
    final book = state.valueOrNull ?? loaded;
    final next = change(book);
    if (identical(next, book)) return;
    state = AsyncData(next);
    try {
      await _repo.saveLessonResume(next);
    } catch (_) {
      // A failed write only costs the resume point; never break the lesson.
    }
  }
}

final lessonResumeProvider =
    AsyncNotifierProvider<LessonResumeController, LessonResumeBook>(
      LessonResumeController.new,
    );
