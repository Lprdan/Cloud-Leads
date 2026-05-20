from typing import Dict, Any, List

class SalesGenerator:
    @staticmethod
    def generate_approach(business_name: str, score_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generates a personalized sales suggestion based on the lead's specific gaps.
        """
        reasons = score_data.get("reasons", [])
        rating = analysis.get("rating", 0)

        # Templates based on the primary gap
        if "No professional website found" in reasons:
            if rating >= 4.0:
                return (f"A empresa {business_name} tem uma ótima reputação ({rating}★), mas não possui site. "
                        "Abordagem: Ofereça uma landing page de alta conversão com integração de WhatsApp para "
                        "capturar a demanda existente e transformá-la em vendas automatizadas.")
            else:
                return (f"A empresa {business_name} carece de presença digital. "
                        "Abordagem: Ofereça um pacote de 'Identidade Digital': um site profissional "
                        "para gerar confiança e um Perfil do Google otimizado para atrair mais clientes locais.")

        if "Missing Instagram/Social presence" in reasons:
            return (f"A empresa {business_name} não possui canais de redes sociais. "
                    "Abordagem: Sugira um pacote de gestão de redes sociais focado em Instagram e "
                    "TikTok para alcançar um público local mais jovem e exibir seus produtos visualmente.")

        if "Limited visual content (photos)" in reasons:
            return (f"A empresa {business_name} tem um perfil visual fraco. "
                    "Abordagem: Ofereça uma sessão de fotografia profissional e um site com galeria visual "
                    "para destacar a qualidade do trabalho.")

        return (f"Abordagem {business_name}: Auditoria digital geral e otimização para melhorar "
                "a visibilidade online e as taxas de conversão.")

generator = SalesGenerator()
