using HtmlAgilityPack;
using MongoDB.Bson;
using MongoDB.Driver;
using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace WebCrawler
{
    internal class Program
    {
        protected static IMongoClient _client;
        protected static IMongoDatabase _database;
        protected static IMongoCollection<NewsData> _collection;

        private static List<string> startUrls;
        private static string pageExtension = "-page";
        private static string currentEndUrl;
        private static string resultLink;
        private static string validXPath;
        private static int currentListIndex;

        private static List<string> urlList;
        private static HttpClient httpClient;
        private static HtmlDocument htmlDoc;
        private static MD5 md5;

        private static void Main(string[] args)
        {
            startUrls.Add("http://www.jagran.com/search/news");
            startUrls.Add("http://www.jagran.com/news/sports-news-hindi");
            startUrls.Add("http://www.jagran.com/news/national-news-hindi");
            startUrls.Add("http://www.jagran.com/news/world-news-hindi");

            _client = new MongoClient("mongodb://localhost");
            _database = _client.GetDatabase("JagranCSharp");
            try
            {
                _database.CreateCollection("News");
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Console.WriteLine("Index already created");
            }
            _collection = _database.GetCollection<NewsData>("News");

            urlList = new List<string>();

            httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("user-agent",
                "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0");

            htmlDoc = new HtmlDocument();
            md5 = new MD5CryptoServiceProvider();

            CreateIndex();
            MainSimulator();

            Console.ReadKey();
        }

        private static async void CreateIndex()
        {
            await _collection.Indexes.CreateOneAsync(Builders<NewsData>.IndexKeys.Ascending(_ => _.hash));
        }

        private static void WriteUrlToFile(string link)
        {
            Console.WriteLine("Writing URL to file");
            if (!File.Exists("JagranLastUrl.txt"))
                using (FileStream fs = File.Create("JagranLastUrl.txt")) { };
            File.WriteAllText("JagranLastUrl.txt", link);
        }

        private static void WriteLogsToFile(string link, bool success, string reason)
        {
            if (!File.Exists("JagranLogs.txt"))
                using (FileStream fs = File.Create("JagranLogs.txt")) { };

            using (StreamWriter sw = File.AppendText("JagranLogs.txt"))
            {
                if (success)
                    sw.WriteLine("All Completed. Got All links!!!");
                else
                {
                    sw.WriteLine("URL: {0}", link);
                    sw.WriteLine("Reason: {0}", reason);
                }
                DateTime now = DateTime.Now;
                sw.WriteLine("Current Time: " + now);
                if (success)
                    sw.WriteLine();
            }
        }

        private static async Task<bool> GetLinksFromPage(string link, bool writeToFile)
        {
            try
            {
                urlList.Clear();
                Console.WriteLine("Getting Page: {0}", link);
                HttpResponseMessage response = await httpClient.GetAsync(link);
                response.EnsureSuccessStatusCode();
                string pageContent = await response.Content.ReadAsStringAsync();
                htmlDoc.LoadHtml(pageContent);

                foreach (HtmlNode links in htmlDoc.DocumentNode.SelectNodes(validXPath))
                    urlList.Add("http://www.jagran.com" + links.GetAttributeValue("href", ""));

                if (urlList.Count == 0)
                {
                    WriteUrlToFile(currentEndUrl);
                    return false;
                }
                if (writeToFile)
                    WriteUrlToFile(link);
                return true;
            }
            catch (Exception e)
            {
                Console.WriteLine("Exception in getting links from page");
                Console.Write(e.Message);
                WriteLogsToFile(link, false, e.Message);
                return false;
            }
        }

        private static async Task GetInfoFromPage(string link)
        {
            try
            {
                Console.WriteLine("Getting Page {0}", link);
                HttpResponseMessage response = await httpClient.GetAsync(link);
                response.EnsureSuccessStatusCode();
                string pageContent = await response.Content.ReadAsStringAsync();
                htmlDoc.LoadHtml(pageContent);
                try
                {
                    NewsData newsData = new NewsData();
                    HtmlNode lastModifiedNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//meta[@http-equiv=\"Last-Modified\"]");
                    string lastModified = lastModifiedNode.GetAttributeValue("content", "None");
                    DateTimeOffset lastModifiedDate = DateTimeOffset.ParseExact(lastModified, "yyyy-MM-ddTHH:mm:sszzz", null);
                    newsData.lastModified = lastModifiedDate.UtcDateTime;

                    HtmlNode titleNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//section[@class=\"title\"]/h1");
                    string title = titleNode.InnerText;
                    newsData.title = title;

                    HtmlNode metaTitleNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//meta[@property=\"og:title\"]");
                    string metaTitle = metaTitleNode.GetAttributeValue("content", "");
                    newsData.metaTitle = metaTitle;

                    HtmlNode keyWordsNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//meta[@name=\"keywords\"]");
                    string[] keyWords = keyWordsNode.GetAttributeValue("content", "").Split(',');
                    for (int i = 0; i < keyWords.Length; i++)
                        keyWords[i] = keyWords[i].Trim();
                    newsData.keywords = keyWords;

                    string url = link;
                    newsData.url = url;

                    HtmlNode summaryNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//div[@class=\"article-summery\"]");
                    string summary = summaryNode.InnerText;
                    newsData.summary = summary;

                    HtmlNode metaDescriptionNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//meta[@property=\"og:description\"]");
                    string metaDescription = metaDescriptionNode.GetAttributeValue("content", "");
                    newsData.metaDescription = metaDescription;

                    HtmlNode imageNode = htmlDoc.DocumentNode.
                        SelectSingleNode("//div[@id=\"jagran_image_id\"]/img");
                    string imageUrl = imageNode.GetAttributeValue("src", "");
                    newsData.image = imageUrl;

                    string allDescriptions = "";
                    foreach (HtmlNode descriptions in htmlDoc.DocumentNode.
                        SelectNodes("//div[@class=\"article-content\"]/p"))
                        allDescriptions += descriptions.InnerText;
                    newsData.description = allDescriptions;

                    byte[] stringToHash = Encoding.UTF8.GetBytes(metaTitle + metaDescription);
                    byte[] hashBytes = md5.ComputeHash(stringToHash);
                    string hash = BitConverter.ToString(hashBytes);
                    newsData.hash = hash;

                    AddToDataBase(newsData);
                }
                catch (Exception e)
                {
                    Console.WriteLine("Exception in extracting info from page");
                    Console.WriteLine(e.Message);
                    WriteLogsToFile(link, false, e.Message);
                    return;
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Exception in getting info from page");
                Console.Write(e.Message);
                WriteLogsToFile(link, false, e.Message);
                return;
            }
        }

        private static async void AddToDataBase(NewsData newsData)
        {
            Console.WriteLine("Adding data {0} to database...", newsData.image);
            FindOptions<NewsData> options = new FindOptions<NewsData> { Limit = 1 };
            IAsyncCursor<NewsData> task = await _collection.FindAsync(x => x.hash.Equals(newsData.hash), options);
            NewsData result = task.FirstOrDefault();
            if (result != null)
            {
                Console.WriteLine("Page Already Added...");
                return;
            }
            else
                await _collection.InsertOneAsync(newsData);
            Console.WriteLine("Data Added!!!");
        }

        private static async void MainSimulator()
        {
            for (int j = 0; j < startUrls.Count; j++)
            {
                currentListIndex = j;
                if (j == 0)
                {
                    resultLink = startUrls[j];
                    validXPath = "//ul[@class=\"listing\"]/li/h3/a[@href]";
                }
                else
                {
                    resultLink = startUrls[j] + ".html";
                    validXPath = "//ul[@class=\"listing\"]/li/h2/a[@href]";
                }

                bool result = await GetLinksFromPage(resultLink, false);
                if (result)
                    for (int i = 0; i < urlList.Count; i++)
                        await GetInfoFromPage(urlList[i]);

                if (File.Exists("JagranLastUrl.txt"))
                    Console.WriteLine("File Exists");
                else
                {
                    Console.WriteLine("File does not exist. Creating file...");
                    using (FileStream fs = File.Create("JagranLastUrl.txt"))
                    {
                        byte[] link;
                        if (j == 0)
                            link = new UTF8Encoding(true).GetBytes(startUrls[j] + pageExtension + "2");
                        else
                            link = new UTF8Encoding(true).GetBytes(startUrls[j] + pageExtension + "2.html");
                        fs.Write(link, 0, link.Length);
                    }
                }

                string fileContents = File.ReadAllText("JagranLastUrl.txt");
                fileContents = fileContents.Trim();
                int counter = 2;
                Regex regex = new Regex(@"\d+");
                Match match = regex.Match(fileContents);
                if (match.Success)
                    counter = int.Parse(match.Value);
                else
                {
                    Console.WriteLine("Match Failed!!!");
                    return;
                }

                while (true)
                {
                    if (j == 0)
                        resultLink = startUrls[j] + pageExtension + counter.ToString();
                    else
                        resultLink = startUrls[j] + pageExtension + counter.ToString() + ".html";

                    result = await GetLinksFromPage(resultLink, true);
                    if (!result)
                        break;
                    for (int i = 0; i < urlList.Count; i++)
                        await GetInfoFromPage(urlList[i]);
                    counter++;
                }
                Console.WriteLine("First Set of URLs done.");
                WriteLogsToFile("", true, "");
            }

            Console.WriteLine("Wowser. All done!!!");
            WriteLogsToFile("", true, "");
        }
    }

    public class NewsData
    {
        public ObjectId _id { get; set; }
        public string title { get; set; }
        public string metaTitle { get; set; }
        public string hash { get; set; }
        public string image { get; set; }
        public string summary { get; set; }
        public string description { get; set; }
        public string metaDescription { get; set; }
        public string url { get; set; }
        public string[] keywords { get; set; }
        public DateTime lastModified { get; set; }
    }
}