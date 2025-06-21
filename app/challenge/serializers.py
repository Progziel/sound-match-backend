import os
import numpy as np
from rest_framework import serializers
from pyAudioAnalysis import audioBasicIO, ShortTermFeatures
from sklearn.metrics.pairwise import cosine_similarity
from core.models import Challenge
from django.conf import settings


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at", "sound_features", "joined_users"]

    def create(self, validated_data):
        """Create Challenge with audio feature extraction"""
        validated_data["created_by"] = self.context["request"].user
        validated_data["sound_features"] = self._process_audio_file(validated_data["sound_url"])
        return super().create(validated_data)

    def _process_audio_file(self, sound_url):
        """Extract audio features from file"""

        path = sound_url.split("/media/")[1]
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(file_path):
            raise serializers.ValidationError({"file_path": "Audio file not found."})

        try:
            Fs, x = audioBasicIO.read_audio_file(file_path)

            if x is None or len(x) == 0:
                raise serializers.ValidationError({"file_path": "Invalid or empty audio file."})

            # Convert to mono
            if len(x.shape) > 1:
                x = x[:, 0]

            # Extract features
            features, _ = ShortTermFeatures.feature_extraction(x, Fs, int(0.050 * Fs), int(0.025 * Fs))

            if features is None or features.shape[0] == 0:
                raise serializers.ValidationError({"file_path": "Feature extraction failed."})

            return [
                float(np.mean(features[0])),  # ZCR
                float(np.mean(features[1])),  # Energy
                float(np.mean(features[2])),  # Spectral Centroid
                float(np.mean(features[7])),  # Clarity
                np.mean(features[8:21], axis=1).tolist(),  # MFCCs
            ]
        except Exception as e:
            raise serializers.ValidationError({"file_path": f"Audio processing failed: {str(e)}"})


class VoiceUpdateSerializer(serializers.Serializer):
    voice_file = serializers.FileField(required=True)

    def validate_voice_file(self, value):
        """Validate uploaded file"""
        if value.size > 50 * 1024 * 1024:  # 50MB
            raise serializers.ValidationError("File too large (max 50MB).")

        if not value.name.lower().endswith('.wav'):
            raise serializers.ValidationError("Only .wav files allowed.")

        return value

    def update_challenge_voice(self, challenge_instance):
        """Process uploaded voice file and compare with challenge"""
        voice_file = self.validated_data["voice_file"]
        temp_path = self._save_temp_file(voice_file, challenge_instance.id)

        try:
            voice_features = self._extract_features(temp_path)
            similarities = self._calculate_similarities(challenge_instance.sound_features, voice_features)
            self._print_results(similarities)
            return challenge_instance
        finally:
            self._cleanup_file(temp_path)

    def _save_temp_file(self, voice_file, challenge_id):
        """Save uploaded file temporarily"""
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"temp_voice_{challenge_id}.wav")

        try:
            with open(temp_path, "wb") as f:
                for chunk in voice_file.chunks():
                    f.write(chunk)
            return temp_path
        except Exception as e:
            raise serializers.ValidationError({"voice_file": f"Failed to save file: {str(e)}"})

    def _extract_features(self, file_path):
        """Extract features from audio file"""
        try:
            Fs, x = audioBasicIO.read_audio_file(file_path)

            if x is None or len(x) == 0:
                raise serializers.ValidationError({"voice_file": "Invalid audio file."})

            # Convert to mono
            if len(x.shape) > 1:
                x = x[:, 0]

            # Extract features
            features, _ = ShortTermFeatures.feature_extraction(x, Fs, int(0.050 * Fs), int(0.025 * Fs))

            if features is None or features.shape[0] == 0:
                raise serializers.ValidationError({"voice_file": "Feature extraction failed."})

            return [
                float(np.mean(features[0])),  # ZCR
                float(np.mean(features[1])),  # Energy
                float(np.mean(features[2])),  # Spectral Centroid
                float(np.mean(features[7])),  # Clarity
                np.mean(features[8:21], axis=1).tolist(),  # MFCCs
            ]
        except Exception as e:
            raise serializers.ValidationError({"voice_file": f"Audio processing failed: {str(e)}"})

    def _calculate_similarities(self, challenge_features, voice_features):
        """Calculate similarity scores between challenge and voice features"""
        # Basic feature similarities
        similarities = {
            'zcr': self._feature_similarity(challenge_features[0], voice_features[0]),
            'energy': self._feature_similarity(challenge_features[1], voice_features[1]),
            'centroid': self._feature_similarity(challenge_features[2], voice_features[2]),
            'clarity': self._feature_similarity(challenge_features[3], voice_features[3]),
        }

        # MFCC similarity using cosine similarity
        challenge_mfcc = np.array(challenge_features[4]).flatten()
        voice_mfcc = np.array(voice_features[4]).flatten()

        similarities['mfcc'] = cosine_similarity(
            challenge_mfcc.reshape(1, -1),
            voice_mfcc.reshape(1, -1)
        )[0, 0]

        return similarities

    @staticmethod
    def _feature_similarity(val1, val2, epsilon=1e-6):
        """Calculate normalized similarity between two values"""
        try:
            return max(0, min(1, 1 - abs(val1 - val2) / (max(val1, val2) + epsilon)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _print_results(similarities):
        """Print similarity results"""
        print(f"Voice Similarity Results:")
        for feature, score in similarities.items():
            print(f"  {feature.upper()}: {score:.3f}")

    @staticmethod
    def _cleanup_file(file_path):
        """Remove temporary file"""
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass