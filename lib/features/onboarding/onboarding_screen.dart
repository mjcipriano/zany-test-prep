import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/exam.dart';

/// Multi-step onboarding: welcome -> offline -> exam -> plan (daily goal +
/// optional test date) -> placement check offer.
///
/// The last step offers the short placement check ("Take the quick check",
/// which finishes onboarding and opens `/diagnostic`) or skips it ("Start
/// learning"; Home keeps offering it until taken or dismissed).
class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;
  String _examId = kDefaultExamId;
  int _goalMinutes = 10;
  DateTime? _targetDate;
  bool _submitting = false;

  static const _pageCount = 5;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _next() {
    if (_page < _pageCount - 1) {
      _controller.nextPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeOutCubic,
      );
    } else {
      _finish();
    }
  }

  Future<void> _finish({bool takeCheck = false}) async {
    // Captured up front: this screen is unmounted as soon as the router sees
    // onboarding complete.
    final router = GoRouter.of(context);
    setState(() => _submitting = true);
    try {
      await ref
          .read(appControllerProvider.notifier)
          .completeOnboarding(
            examId: _examId,
            dailyGoalMinutes: _goalMinutes,
            targetTestDate: _targetDate,
          );
      // Router redirects to /home once onboarded flips to true; the check
      // replaces that with the placement quiz for the chosen exam.
      if (takeCheck) router.go('/diagnostic');
    } catch (e) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Could not load that exam: $e')));
    }
  }

  ExamInfo? _examInfo(List<ExamInfo> exams) {
    for (final e in exams) {
      if (e.id == _examId) return e;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final exams =
        ref.watch(appControllerProvider).valueOrNull?.exams ?? const [];
    // Default to the first shipped exam if the usual default isn't available.
    if (exams.isNotEmpty && !exams.any((e) => e.id == _examId)) {
      _examId = exams.first.id;
    }
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              child: Row(
                children: List.generate(_pageCount, (i) {
                  final active = i <= _page;
                  return Expanded(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 250),
                      height: 6,
                      margin: const EdgeInsets.symmetric(horizontal: 3),
                      decoration: BoxDecoration(
                        color: active
                            ? Theme.of(context).colorScheme.primary
                            : Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  );
                }),
              ),
            ),
            Expanded(
              child: PageView(
                controller: _controller,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (i) => setState(() => _page = i),
                children: [
                  _Welcome(),
                  _OfflineNote(),
                  _ExamStep(
                    exams: exams,
                    selected: _examId,
                    onSelect: (id) => setState(() => _examId = id),
                  ),
                  _GoalStep(
                    selected: _goalMinutes,
                    onSelect: (m) => setState(() => _goalMinutes = m),
                    date: _targetDate,
                    onPickDate: (d) => setState(() => _targetDate = d),
                  ),
                  _PlacementStep(exam: _examInfo(exams)),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: _page == _pageCount - 1
                  ? Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        FilledButton.icon(
                          onPressed: _submitting
                              ? null
                              : () => _finish(takeCheck: true),
                          icon: const Icon(Icons.explore_rounded),
                          label: const Text('Take the quick check'),
                        ),
                        Gap.s,
                        OutlinedButton(
                          onPressed: _submitting ? null : _finish,
                          child: const Text('Start learning'),
                        ),
                      ],
                    )
                  : FilledButton(
                      onPressed: _submitting ? null : _next,
                      child: const Text('Continue'),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Welcome extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return _StepScaffold(
      icon: Icons.school_rounded,
      title: 'Welcome to Zany Test Prep',
      body:
          'Short, game-like lessons that make studying for the SAT or ACT feel '
          'less like a chore. Earn XP, build streaks, and master one skill at a '
          'time.',
      accent: scheme.primary,
    );
  }
}

class _OfflineNote extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const _StepScaffold(
      icon: Icons.wifi_off_rounded,
      title: 'Works completely offline',
      body:
          'Everything you need is on your device. No account, no login, and no '
          'internet required. Your progress is saved locally and stays private.',
      accent: AppTheme.correct,
    );
  }
}

class _ExamStep extends StatelessWidget {
  const _ExamStep({
    required this.exams,
    required this.selected,
    required this.onSelect,
  });
  final List<ExamInfo> exams;
  final String selected;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return _StepScaffold(
      icon: Icons.menu_book_rounded,
      title: 'Choose your exam',
      body:
          'Pick the test you are preparing for. You can switch exams any time '
          'in Settings, and your XP and streak carry across.',
      accent: Theme.of(context).colorScheme.primary,
      child: Column(
        children: [
          for (final exam in exams)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _ChoiceTile(
                label: exam.name,
                subtitle: exam.tagline.isNotEmpty
                    ? '${exam.displayName} — ${exam.tagline}'
                    : (exam.displayName != exam.name
                          ? exam.displayName
                          : 'Prepare for the ${exam.name}'),
                selected: selected == exam.id,
                onTap: () => onSelect(exam.id),
              ),
            ),
          if (exams.isEmpty)
            const _ChoiceTile(
              label: 'SAT',
              subtitle: 'Digital SAT — Reading, Writing & Math',
              selected: true,
              onTap: _noop,
            ),
        ],
      ),
    );
  }

  static void _noop() {}
}

class _GoalStep extends StatelessWidget {
  const _GoalStep({
    required this.selected,
    required this.onSelect,
    required this.date,
    required this.onPickDate,
  });
  final int selected;
  final ValueChanged<int> onSelect;
  final DateTime? date;
  final ValueChanged<DateTime?> onPickDate;

  @override
  Widget build(BuildContext context) {
    return _StepScaffold(
      icon: Icons.flag_rounded,
      title: 'Pick a daily goal',
      body:
          'How many minutes do you want to practice each day? You can change '
          'this anytime in Settings.',
      accent: AppTheme.streak,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final m in const [5, 10, 15])
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _ChoiceTile(
                label: '$m minutes a day',
                subtitle: m == 5
                    ? 'Casual'
                    : m == 10
                    ? 'Regular (recommended)'
                    : 'Serious',
                selected: selected == m,
                onTap: () => onSelect(m),
              ),
            ),
          Gap.s,
          _DatePicker(date: date, onPick: onPickDate),
        ],
      ),
    );
  }
}

/// Optional target test date (part of the daily-goal step).
class _DatePicker extends StatelessWidget {
  const _DatePicker({required this.date, required this.onPick});
  final DateTime? date;
  final ValueChanged<DateTime?> onPick;

  @override
  Widget build(BuildContext context) {
    final d = date;
    return Row(
      children: [
        Expanded(
          child: Text(
            'Test date (optional)',
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
          ),
        ),
        TextButton.icon(
          onPressed: () async {
            final now = DateTime.now();
            final picked = await showDatePicker(
              context: context,
              initialDate: d ?? now.add(const Duration(days: 60)),
              firstDate: now,
              lastDate: now.add(const Duration(days: 365 * 2)),
            );
            if (picked != null) onPick(picked);
          },
          icon: const Icon(Icons.calendar_today_rounded, size: 18),
          label: Text(
            d == null
                ? 'Pick a date'
                : '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}',
          ),
        ),
        if (d != null)
          IconButton(
            tooltip: 'Clear date',
            onPressed: () => onPick(null),
            icon: const Icon(Icons.close_rounded, size: 18),
          ),
      ],
    );
  }
}

/// The last step: offers the short placement check for the chosen exam.
class _PlacementStep extends StatelessWidget {
  const _PlacementStep({required this.exam});
  final ExamInfo? exam;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final name = exam?.name ?? 'your exam';
    return _StepScaffold(
      icon: Icons.explore_rounded,
      title: 'Find your starting point',
      body:
          'Answer 12 quick questions from across the $name so we can see '
          'what you already know and recommend what to study first.',
      accent: scheme.tertiary,
      child: const Column(
        children: [
          _Bullet(icon: Icons.timer_outlined, text: 'About 3 minutes'),
          _Bullet(
            icon: Icons.sentiment_satisfied_alt_rounded,
            text: 'No XP at stake and no penalties: just your best guess',
          ),
          _Bullet(
            icon: Icons.skip_next_rounded,
            text: 'Optional: skip it now and take it later from Home',
          ),
        ],
      ),
    );
  }
}

class _Bullet extends StatelessWidget {
  const _Bullet({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: scheme.tertiary, size: 22),
          Gap.s,
          Expanded(
            child: Text(text, style: Theme.of(context).textTheme.bodyLarge),
          ),
        ],
      ),
    );
  }
}

class _StepScaffold extends StatelessWidget {
  const _StepScaffold({
    required this.icon,
    required this.title,
    required this.body,
    required this.accent,
    this.child,
  });

  final IconData icon;
  final String title;
  final String body;
  final Color accent;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Gap.l,
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: accent.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 48, color: accent),
          ),
          Gap.l,
          Text(
            title,
            style: Theme.of(
              context,
            ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
          ),
          Gap.s,
          Text(
            body,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          if (child != null) ...[Gap.l, child!],
        ],
      ),
    );
  }
}

class _ChoiceTile extends StatelessWidget {
  const _ChoiceTile({
    required this.label,
    required this.subtitle,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AppCard(
      onTap: onTap,
      color: selected ? scheme.primaryContainer : scheme.surfaceContainerHigh,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(color: scheme.onSurfaceVariant),
                ),
              ],
            ),
          ),
          Icon(
            selected
                ? Icons.check_circle_rounded
                : Icons.radio_button_unchecked_rounded,
            color: selected ? scheme.primary : scheme.outline,
          ),
        ],
      ),
    );
  }
}
