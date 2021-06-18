from django.db.models import Count
from .models import ExperimentVariant, ExperimentVariantParticipant


class VariantSelector:
    @staticmethod
    def choose_variant(experiment):
        total_participants = VariantSelector.get_total_participants(experiment)
        if total_participants == 0:
            return ExperimentVariant.objects.order_by('?').first()

        variant_data = VariantSelector.get_variant_data(experiment)
        variant_predefined_ratios_by_name_dict = VariantSelector.create_variant_predefined_ratios_by_name_dict(
            variant_data)
        variant_actual_ratios_by_name_dict = VariantSelector.create_variant_actual_ratios_by_name_dict(variant_data,
                                                                                                       total_participants)
        variant_deviation_dict = VariantSelector.create_variant_deviation_dict(variant_predefined_ratios_by_name_dict,
                                                                               variant_actual_ratios_by_name_dict)

        return VariantSelector.get_highest_deviation_variant(variant_deviation_dict)

    @staticmethod
    def get_total_participants(experiment):
        return ExperimentVariantParticipant.objects.count()

    @staticmethod
    def get_variant_data(experiment):
        return ExperimentVariant.objects.filter(experiment=experiment).annotate(
            participents_num=Count('experimentvariantparticipant'))

    @staticmethod
    def create_variant_predefined_ratios_by_name_dict(variant_data):
        return {variant.name: variant.ratio for variant in variant_data}

    @staticmethod
    def create_variant_actual_ratios_by_name_dict(variant_data, total_participants):
        return {variant.name: (variant.participents_num / total_participants * 100) for variant in variant_data}

    @staticmethod
    def create_variant_deviation_dict(variant_predefined_ratios_by_name_dict, variant_actual_ratios_by_name_dict):
        return {key: (variant_predefined_ratios_by_name_dict[key] - variant_actual_ratios_by_name_dict[key]) for key in
                variant_predefined_ratios_by_name_dict}

    @staticmethod
    def get_highest_deviation_variant(variant_deviation_dict):
        highest_deviation_variant = {'name': 'error', 'deviation': -100}
        for key in variant_deviation_dict:
            if variant_deviation_dict[key] > highest_deviation_variant['deviation']:
                highest_deviation_variant = {'name': key, 'deviation': variant_deviation_dict[key]}

        return ExperimentVariant.objects.get(name=highest_deviation_variant['name'])
