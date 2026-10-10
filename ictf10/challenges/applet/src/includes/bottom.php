<?
	if(isset($_SESSION['auth']) && ($_SESSION['auth'] == 1))
	{
?>
	<p align="center">
		<a href="./logout.php">[Logout]</a>
	</p>
<?
	}
?>
		</td>
		<td class="border">&nbsp;</td>
	</tr>
</table>
</body>
</html>

