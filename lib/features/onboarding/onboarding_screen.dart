import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';

/// Multi-step onboarding: welcome -> offline -> exam -> goal -> date -> finish.
class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;
  String _examId = 'sat';
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

  Future<void> _finish() async {
    setState(() => _submitting = true);
    await ref
        .read(appControllerProvider.notifier)
        .completeOnboarding(
          examId: _examId,
          dailyGoalMinutes: _goalMinutes,
          targetTestDate: _targetDate,
        );
    // Router redirects to /home once onboarded flips to true.
  }

  @override
  Widget build(BuildContext context) {
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
                    selected: _examId,
                    onSelect: (id) => setState(() => _examId = id),
                  ),
                  _GoalStep(
                    selected: _goalMinutes,
                    onSelect: (m) => setState(() => _goalMinutes = m),
                  ),
                  _DateStep(
                    date: _targetDate,
                    onPick: (d) => setState(() => _targetDate = d),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: FilledButton(
                onPressed: _submitting ? null : _next,
                child: _submitting
                    ? const SizedBox(
                        height: 22,
                        width: 22,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(
                        _page == _pageCount - 1 ? 'Start learning' : 'Continue',
                      ),
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
          'Short, game-like lessons that make studying for the SAT feel less '
          'like a chore. Earn XP, build streaks, and master one skill at a time.',
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
  const _ExamStep({required this.selected, required this.onSelect});
  final String selected;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return _StepScaffold(
      icon: Icons.menu_book_rounded,
      title: 'Choose your exam',
      body:
          'More exams (ACT, AP) are on the way. For now, let’s focus on the SAT.',
      accent: Theme.of(context).colorScheme.primary,
      child: Column(
        children: [
          _ChoiceTile(
            label: 'SAT',
            subtitle: 'Digital SAT — Reading, Writing & Math',
            selected: selected == 'sat',
            onTap: () => onSelect('sat'),
          ),
          Gap.s,
          _ChoiceTile(
            label: 'ACT (coming soon)',
            subtitle: 'Not available yet',
            selected: false,
            enabled: false,
            onTap: () {},
          ),
        ],
      ),
    );
  }
}

class _GoalStep extends StatelessWidget {
  const _GoalStep({required this.selected, required this.onSelect});
  final int selected;
  final ValueChanged<int> onSelect;

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
        ],
      ),
    );
  }
}

class _DateStep extends StatelessWidget {
  const _DateStep({required this.date, required this.onPick});
  final DateTime? date;
  final ValueChanged<DateTime?> onPick;

  @override
  Widget build(BuildContext context) {
    return _StepScaffold(
      icon: Icons.event_rounded,
      title: 'When is your test?',
      body: 'Set a target test date to stay motivated — or skip it for now.',
      accent: Theme.of(context).colorScheme.tertiary,
      child: Column(
        children: [
          OutlinedButton.icon(
            onPressed: () async {
              final now = DateTime.now();
              final picked = await showDatePicker(
                context: context,
                initialDate: date ?? now.add(const Duration(days: 60)),
                firstDate: now,
                lastDate: now.add(const Duration(days: 365 * 2)),
              );
              if (picked != null) onPick(picked);
            },
            icon: const Icon(Icons.calendar_today_rounded),
            label: Text(
              date == null
                  ? 'Pick a date'
                  : '${date!.year}-${date!.month.toString().padLeft(2, '0')}-${date!.day.toString().padLeft(2, '0')}',
            ),
          ),
          if (date != null)
            TextButton(
              onPressed: () => onPick(null),
              child: const Text('Clear date'),
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
    this.enabled = true,
  });

  final String label;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Opacity(
      opacity: enabled ? 1 : 0.5,
      child: AppCard(
        onTap: enabled ? onTap : null,
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
      ),
    );
  }
}
