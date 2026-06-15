import 'package:flutter/material.dart';

import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/question.dart';

/// Renders a single question and its input. Stateless: the player owns state.
class QuestionView extends StatelessWidget {
  const QuestionView({
    super.key,
    required this.question,
    required this.answered,
    required this.selectedChoiceId,
    required this.textController,
    required this.onSelectChoice,
  });

  final Question question;
  final bool answered;
  final String? selectedChoiceId;
  final TextEditingController textController;
  final ValueChanged<String> onSelectChoice;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: kPagePadding,
      children: [
        if (question.stimulus != null) ...[
          _StimulusView(stimulus: question.stimulus!),
          Gap.m,
        ],
        Text(
          question.prompt,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
            height: 1.3,
          ),
        ),
        Gap.l,
        if (question.type.isStudentProduced)
          _ProducedInput(controller: textController, answered: answered)
        else
          ...question.choices.map(
            (c) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _ChoiceButton(
                choice: c,
                selected: selectedChoiceId == c.id,
                answered: answered,
                isCorrect: c.id == question.correctChoice,
                onTap: answered ? null : () => onSelectChoice(c.id),
              ),
            ),
          ),
      ],
    );
  }
}

class _ChoiceButton extends StatelessWidget {
  const _ChoiceButton({
    required this.choice,
    required this.selected,
    required this.answered,
    required this.isCorrect,
    required this.onTap,
  });

  final Choice choice;
  final bool selected;
  final bool answered;
  final bool isCorrect;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    Color border = scheme.outlineVariant;
    Color bg = scheme.surfaceContainerHigh;
    final Color fg = scheme.onSurface;
    IconData? trailing;

    if (answered) {
      if (isCorrect) {
        border = AppTheme.correct;
        bg = AppTheme.correct.withValues(alpha: 0.14);
        trailing = Icons.check_circle_rounded;
      } else if (selected) {
        border = AppTheme.incorrect;
        bg = AppTheme.incorrect.withValues(alpha: 0.12);
        trailing = Icons.cancel_rounded;
      }
    } else if (selected) {
      border = scheme.primary;
      bg = scheme.primaryContainer;
    }

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: border, width: 2),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            child: Row(
              children: [
                Container(
                  width: 30,
                  height: 30,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: border, width: 2),
                  ),
                  child: Text(
                    choice.id,
                    style: TextStyle(fontWeight: FontWeight.w800, color: fg),
                  ),
                ),
                Gap.m,
                Expanded(
                  child: Text(
                    choice.text,
                    style: TextStyle(fontSize: 16, color: fg),
                  ),
                ),
                if (trailing != null)
                  Icon(
                    trailing,
                    color: isCorrect ? AppTheme.correct : AppTheme.incorrect,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProducedInput extends StatelessWidget {
  const _ProducedInput({required this.controller, required this.answered});
  final TextEditingController controller;
  final bool answered;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Enter your answer',
          style: Theme.of(context).textTheme.labelLarge,
        ),
        Gap.s,
        TextField(
          controller: controller,
          enabled: !answered,
          keyboardType: const TextInputType.numberWithOptions(
            decimal: true,
            signed: true,
          ),
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          decoration: InputDecoration(
            hintText: 'e.g. 12 or 3/4',
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ),
      ],
    );
  }
}

class _StimulusView extends StatelessWidget {
  const _StimulusView({required this.stimulus});
  final Stimulus stimulus;

  @override
  Widget build(BuildContext context) {
    if (stimulus.isTable && stimulus.table != null) {
      final t = stimulus.table!;
      return AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (t.caption != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  t.caption!,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: [
                  for (final h in t.headers)
                    DataColumn(
                      label: Text(
                        h,
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ),
                ],
                rows: [
                  for (final r in t.rows)
                    DataRow(cells: [for (final c in r) DataCell(Text(c))]),
                ],
              ),
            ),
          ],
        ),
      );
    }
    if (stimulus.isPaired) {
      return Column(
        children: [
          _PassageCard(title: 'Text 1', text: stimulus.text ?? ''),
          Gap.s,
          _PassageCard(title: 'Text 2', text: stimulus.textB ?? ''),
        ],
      );
    }
    return _PassageCard(
      title: stimulus.title ?? 'Passage',
      text: stimulus.text ?? '',
    );
  }
}

class _PassageCard extends StatelessWidget {
  const _PassageCard({required this.title, required this.text});
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AppCard(
      color: scheme.surfaceContainer,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
              color: scheme.primary,
              fontWeight: FontWeight.w800,
            ),
          ),
          Gap.s,
          Text(text, style: const TextStyle(fontSize: 15.5, height: 1.5)),
        ],
      ),
    );
  }
}
