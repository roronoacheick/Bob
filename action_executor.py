import webbrowser
from urllib.parse import quote_plus


class ActionExecutor:
    def __init__(self):
        self.avaible_actions ={
            "open_website": self.open_website,
            "search_youtube": self.search_youtube,
        }


    @staticmethod
    def open_website(url):
        if not url.startswith("https://"):
            return f"Action refusée : l'URL doit commencer par https:// (reçu : {url})"

        webbrowser.open(url)
        return f"Site ouvert : {url}"


    @staticmethod
    def search_youtube(search_query):
        youtube_search_url = "https://www.youtube.com/results?search_query=" + quote_plus(search_query)
        webbrowser.open(youtube_search_url)

        return f"Recherche Youtube ouverte pour: {search_query}"



    def execute_action(self, tool_name, tool_arguments):
        if tool_name not in self.avaible_actions:
            return f"Action inconnue : {tool_name}"

        action = self.avaible_actions[tool_name]
        return action(**tool_arguments)


    @staticmethod
    def build_tool_description(tool_name,tool_description,parameter_name,parameter_description):
         return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        parameter_name: {
                            "type": "string",
                            "description": parameter_description,
                        }
                    },
                    "required": [parameter_name],
                },
            },
        }


    @staticmethod
    def get_tools_description():
        return [
            ActionExecutor.build_tool_description(
                tool_name="open_website",
                tool_description="Ouvre un site web dans le navigateur. À utiliser quand l'utilisateur demande d'ouvrir un site (ex : ouvre YouTube, ouvre Wikipédia).",
                parameter_name="url",
                parameter_description="URL complète du site, qui commence obligatoirement par https:// (ex : https://www.youtube.com)",
            ),
            ActionExecutor.build_tool_description(
                tool_name="search_youtube",
                tool_description="Lance une recherche de vidéos sur YouTube. À utiliser quand l'utilisateur veut voir ou chercher des vidéos sur un sujet. Ne pas utiliser pour ouvrir simplement la page d'accueil de YouTube.",
                parameter_name="search_query",
                parameter_description="Les mots-clés à rechercher (ex : recettes de mafé)",
            ),
        ]
if __name__ == "__main__":
    action_executor_object = ActionExecutor()

    print(action_executor_object.execute_action("open_website", {"url": "https://fr.wikipedia.org"}))
    print(action_executor_object.execute_action("search_youtube", {"search_query": "recettes de curry"}))

    # Cas qui doivent être bloqués
    print(action_executor_object.execute_action("open_website", {"url": "file:///etc/hosts"}))
    print(action_executor_object.execute_action("delete_all_files", {}))